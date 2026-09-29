from app.config import settings


class QueryRewriterAgent:
    async def run(self, *, question: str) -> str:
        prompt = (
            "Rewrite this question for enterprise document retrieval. Keep all named entities, dates, "
            "policy terms, and constraints. Return one concise search query.\n\n"
            f"Question: {question}"
        )

        if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=settings.openai_api_key)
                response = await client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                )
                content = response.choices[0].message.content
                if content:
                    return content.strip()
            except Exception:
                pass

        return f"{question.strip()} relevant policy evidence source page"
