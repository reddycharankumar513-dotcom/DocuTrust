from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, TypedDict

from app.agents.answer_generator_agent import AnswerGeneratorAgent
from app.agents.citation_agent import CitationAgent
from app.agents.grading_agent import GradingAgent
from app.agents.query_rewriter_agent import QueryRewriterAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.web_search_agent import WebSearchAgent
from app.config import settings
from app.schemas.chat import AgentLog
from app.utils.text import contains_prompt_injection, normalize_question
from app.vectorstore.chroma import RetrievedChunk


LogEmitter = Callable[[AgentLog], Awaitable[None]]


class GraphState(TypedDict, total=False):
    question: str
    user_id: str
    documents: list[RetrievedChunk]
    generation: str
    web_search_needed: bool
    rewritten_query: str
    retrieval_score: float
    sources: list[Any]
    top_k: int
    emit: LogEmitter | None


class CorrectiveRAGGraph:
    def __init__(self) -> None:
        self.retriever = RetrievalAgent()
        self.grader = GradingAgent()
        self.rewriter = QueryRewriterAgent()
        self.web_search = WebSearchAgent()
        self.generator = AnswerGeneratorAgent()
        self.citations = CitationAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        try:
            from langgraph.graph import END, START, StateGraph
        except Exception:
            return None

        workflow = StateGraph(GraphState)
        workflow.add_node("query", self._query_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("grade", self._grade_node)
        workflow.add_node("rewrite", self._rewrite_node)
        workflow.add_node("web_search", self._web_search_node)
        workflow.add_node("generate", self._generate_node)

        workflow.add_edge(START, "query")
        workflow.add_edge("query", "retrieve")
        workflow.add_edge("retrieve", "grade")
        workflow.add_conditional_edges(
            "grade",
            self._route_after_grade,
            {"generate": "generate", "rewrite": "rewrite"},
        )
        workflow.add_edge("rewrite", "web_search")
        workflow.add_edge("web_search", "generate")
        workflow.add_edge("generate", END)
        return workflow.compile()

    async def run(self, *, user_id: str, question: str, top_k: int, emit: LogEmitter | None = None) -> GraphState:
        state: GraphState = {
            "question": question,
            "user_id": user_id,
            "documents": [],
            "generation": "",
            "web_search_needed": False,
            "rewritten_query": "",
            "retrieval_score": 0.0,
            "top_k": top_k,
            "emit": emit,
        }

        if self.graph:
            result = await self.graph.ainvoke(state)
        else:
            result = await self._run_sequential(state)

        result.pop("emit", None)
        return result

    async def _run_sequential(self, state: GraphState) -> GraphState:
        state.update(await self._query_node(state))
        state.update(await self._retrieve_node(state))
        state.update(await self._grade_node(state))
        if self._route_after_grade(state) == "rewrite":
            state.update(await self._rewrite_node(state))
            state.update(await self._web_search_node(state))
        state.update(await self._generate_node(state))
        return state

    async def _query_node(self, state: GraphState) -> GraphState:
        question = normalize_question(state["question"])
        await self._emit(state, "Query Node", "running", "Validating question and guardrails.")
        if contains_prompt_injection(question):
            await self._emit(state, "Query Node", "warning", "Potential prompt injection language detected and isolated.")
        return {"question": question}

    async def _retrieve_node(self, state: GraphState) -> GraphState:
        await self._emit(state, "Retriever Node", "running", "Retrieving documents...")
        documents = await self.retriever.run(
            user_id=state["user_id"],
            question=state["question"],
            top_k=state.get("top_k", settings.retrieval_top_k),
        )
        await self._emit(state, "Retriever Node", "completed", f"Retrieved {len(documents)} candidate chunks.")
        return {"documents": documents}

    async def _grade_node(self, state: GraphState) -> GraphState:
        await self._emit(state, "Grading Node", "running", "Re-ranking chunks...")
        retrieval_score, documents = await self.grader.run(question=state["question"], documents=state.get("documents", []))
        web_search_needed = retrieval_score < settings.relevance_threshold
        message = "Checking relevance..."
        await self._emit(state, "Grading Node", "completed", f"{message} Score: {retrieval_score:.2f}.")
        return {
            "documents": documents,
            "retrieval_score": retrieval_score,
            "web_search_needed": web_search_needed,
        }

    def _route_after_grade(self, state: GraphState) -> str:
        return "rewrite" if state.get("web_search_needed") else "generate"

    async def _rewrite_node(self, state: GraphState) -> GraphState:
        await self._emit(state, "Query Rewriter", "running", "Rewriting query...")
        rewritten_query = await self.rewriter.run(question=state["question"])
        await self._emit(state, "Query Rewriter", "completed", "Query rewritten for broader retrieval.")
        return {"rewritten_query": rewritten_query}

    async def _web_search_node(self, state: GraphState) -> GraphState:
        await self._emit(state, "Web Search Agent", "running", "Searching web...")
        query = state.get("rewritten_query") or state["question"]
        web_documents = await self.web_search.run(query=query, user_id=state["user_id"])
        documents = [*state.get("documents", []), *web_documents]
        status = "completed" if web_documents else "warning"
        message = f"Added {len(web_documents)} web evidence chunks." if web_documents else "No web evidence added."
        await self._emit(state, "Web Search Agent", status, message)
        return {"documents": documents}

    async def _generate_node(self, state: GraphState) -> GraphState:
        await self._emit(state, "Answer Generator", "running", "Generating answer...")
        documents = state.get("documents", [])
        generation = await self.generator.run(question=state["question"], documents=documents)
        sources = self.citations.run(documents=documents)
        await self._emit(state, "Citation Agent", "completed", "Attached source filenames and page numbers.")
        await self._emit(state, "Workflow", "completed", "Completed.")
        return {"generation": generation, "sources": sources}

    @staticmethod
    async def _emit(state: GraphState, step: str, status: str, message: str) -> None:
        emitter = state.get("emit")
        if not emitter:
            return
        await emitter(
            AgentLog(
                step=step,
                status=status,
                message=message,
                timestamp=datetime.now(UTC),
            )
        )
