import { useCallback, useEffect, useState } from "react";
import { LogOut, RefreshCcw, ShieldCheck } from "lucide-react";
import { AgentTimeline } from "@/components/AgentTimeline";
import { AuthScreen } from "@/components/AuthScreen";
import { ChatPanel } from "@/components/ChatPanel";
import { CitationList } from "@/components/CitationList";
import { DashboardCards } from "@/components/DashboardCards";
import { DocumentList } from "@/components/DocumentList";
import { GraphVisualizer } from "@/components/GraphVisualizer";
import { RecentChats } from "@/components/RecentChats";
import { UploadPanel } from "@/components/UploadPanel";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useChatSocket } from "@/hooks/useChatSocket";
import {
  askChat,
  deleteDocument,
  exportChatPdf,
  getDashboard,
  getHistory,
  listDocuments,
  setChatFavorite,
  uploadDocuments
} from "@/services/api";
import type { AgentLog, ChatResponse, Dashboard, DocumentRecord } from "@/types";

export default function App() {
  const { token, user, isBooting, signOut } = useAuth();
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [history, setHistory] = useState<ChatResponse[]>([]);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [activeChat, setActiveChat] = useState<ChatResponse | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!token) {
      return;
    }
    const [documentData, historyData, dashboardData] = await Promise.all([
      listDocuments(),
      getHistory(),
      getDashboard()
    ]);
    setDocuments(documentData);
    setHistory(historyData);
    setDashboard(dashboardData);
    setActiveChat((current) => current ?? historyData[0] ?? null);
  }, [token]);

  useEffect(() => {
    refresh().catch((err) => setError(err instanceof Error ? err.message : "Failed to load workspace"));
  }, [refresh]);

  const onLog = useCallback((log: AgentLog) => {
    setLogs((current) => [...current, log]);
  }, []);

  const onChunk = useCallback((chunk: string) => {
    setActiveChat((current) => (current ? { ...current, answer: current.answer + chunk } : current));
  }, []);

  const onAnswer = useCallback(
    (answer: ChatResponse) => {
      setActiveChat(answer);
      setHistory((current) => [answer, ...current.filter((chat) => chat.id !== answer.id)]);
      setIsStreaming(false);
      getDashboard().then(setDashboard).catch(() => undefined);
    },
    []
  );

  const { connected, sendQuestion } = useChatSocket(token, onLog, onChunk, onAnswer);

  async function handleUpload(files: FileList) {
    setError(null);
    await uploadDocuments(files);
    await refresh();
  }

  async function handleDelete(id: string) {
    setError(null);
    await deleteDocument(id);
    await refresh();
  }

  async function handleAsk(question: string) {
    setError(null);
    setLogs([]);
    setIsStreaming(true);
    setActiveChat({
      question,
      answer: "",
      sources: [],
      retrieval_score: 0,
      web_search_used: false,
      logs: [],
      timestamp: new Date().toISOString()
    });

    const sent = sendQuestion(question, 6);
    if (sent) {
      return;
    }

    try {
      const answer = await askChat(question, 6);
      setLogs(answer.logs);
      onAnswer(answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat request failed");
      setIsStreaming(false);
    }
  }

  async function exportChat() {
    if (!activeChat) {
      return;
    }
    if (activeChat.id) {
      const blob = await exportChatPdf(activeChat.id);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `docutrust-chat-${activeChat.id}.pdf`;
      anchor.click();
      URL.revokeObjectURL(url);
      return;
    }

    const content = [
      `Question: ${activeChat.question}`,
      "",
      activeChat.answer,
      "",
      "Sources:",
      ...activeChat.sources.map((source) => `- ${source.filename}${source.page ? `, page ${source.page}` : ""}`)
    ].join("\n");
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "docutrust-chat-export.txt";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function toggleFavorite() {
    if (!activeChat?.id) {
      return;
    }
    const favorite = !activeChat.favorite;
    try {
      await setChatFavorite(activeChat.id, favorite);
      setActiveChat((current) => (current ? { ...current, favorite } : current));
      setHistory((current) => current.map((chat) => (chat.id === activeChat.id ? { ...chat, favorite } : chat)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update favorite");
    }
  }

  if (isBooting) {
    return (
      <main className="grid min-h-screen place-items-center">
        <div className="loading-mark" />
      </main>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  return (
    <main className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-border bg-background/90 backdrop-blur">
        <div className="mx-auto flex max-w-[1560px] items-center justify-between px-4 py-3 lg:px-6">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-card border border-primary/40 bg-primary/15 text-blue-100">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">DocuTrust</h1>
              <p className="text-xs text-muted">Enterprise Advanced RAG Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button aria-label="Refresh dashboard" title="Refresh dashboard" size="icon" variant="ghost" onClick={() => refresh()}>
              <RefreshCcw className="h-4 w-4" />
            </Button>
            <span className="hidden text-sm text-slate-300 sm:inline">{user.name}</span>
            <Button aria-label="Sign out" title="Sign out" size="icon" variant="ghost" onClick={signOut}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1560px] gap-4 px-4 py-4 lg:grid-cols-[360px_minmax(0,1fr)] lg:px-6">
        <aside className="space-y-4">
          <UploadPanel onUpload={handleUpload} />
          <DocumentList documents={documents} onDelete={handleDelete} />
          <RecentChats chats={history} onSelect={setActiveChat} />
        </aside>

        <section className="min-w-0 space-y-4">
          <DashboardCards dashboard={dashboard} />
          <GraphVisualizer activeWebFallback={Boolean(activeChat?.web_search_used)} />
          {error ? <div className="rounded-card border border-danger/40 bg-danger/10 p-3 text-sm text-red-100">{error}</div> : null}
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <ChatPanel
              activeChat={activeChat}
              isStreaming={isStreaming}
              onAsk={handleAsk}
              onExport={exportChat}
              onFavorite={toggleFavorite}
            />
            <div className="space-y-4">
              <AgentTimeline logs={logs.length ? logs : activeChat?.logs ?? []} connected={connected} />
              <CitationList sources={activeChat?.sources ?? []} />
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
