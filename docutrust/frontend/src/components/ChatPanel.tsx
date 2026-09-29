import { FormEvent, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Download, Send, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";
import { Textarea } from "@/components/ui/textarea";
import type { ChatResponse } from "@/types";

type ChatPanelProps = {
  activeChat: ChatResponse | null;
  isStreaming: boolean;
  onAsk: (question: string) => void;
  onExport: () => void;
  onFavorite: () => void;
};

export function ChatPanel({ activeChat, isStreaming, onAsk, onExport, onFavorite }: ChatPanelProps) {
  const [question, setQuestion] = useState("");
  const answer = activeChat?.answer ?? "";
  const retrieval = activeChat ? Math.round(activeChat.retrieval_score * 100) : 0;
  const webUsed = Boolean(activeChat?.web_search_used);

  const meta = useMemo(() => {
    if (!activeChat) {
      return "Ready";
    }
    return webUsed ? "Corrected with fallback" : "Grounded in documents";
  }, [activeChat, webUsed]);

  function submit(event: FormEvent) {
    event.preventDefault();
    const cleanQuestion = question.trim();
    if (!cleanQuestion) {
      return;
    }
    onAsk(cleanQuestion);
    setQuestion("");
  }

  return (
    <Panel className="flex min-h-[560px] flex-1 flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-border px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-white">Chat Interface</h2>
          <p className="text-sm text-muted">{meta}</p>
        </div>
        <div className="flex items-center gap-2">
          {activeChat ? <Badge tone={webUsed ? "amber" : "teal"}>{retrieval}% retrieval</Badge> : null}
          <Button
            aria-label="Favorite answer"
            title="Favorite answer"
            size="icon"
            variant="ghost"
            disabled={!activeChat?.id}
            onClick={onFavorite}
          >
            <Star className="h-4 w-4" fill={activeChat?.favorite ? "currentColor" : "none"} />
          </Button>
          <Button aria-label="Export chat" title="Export chat" size="icon" variant="ghost" onClick={onExport}>
            <Download className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-5">
        {activeChat ? (
          <div className="space-y-4">
            <div className="chat-bubble question">{activeChat.question}</div>
            <article className="chat-bubble answer prose prose-invert max-w-none">
              {answer ? <ReactMarkdown>{answer}</ReactMarkdown> : <span className="text-sm text-muted">Building grounded answer...</span>}
            </article>
          </div>
        ) : (
          <div className="grid h-full place-items-center text-center">
            <div>
              <p className="text-lg font-semibold text-white">No active conversation</p>
              <p className="mt-2 text-sm text-muted">Workspace ready</p>
            </div>
          </div>
        )}
      </div>

      <form className="border-t border-border p-4" onSubmit={submit}>
        <Textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about uploaded documents..."
          disabled={isStreaming}
        />
        <div className="mt-3 flex justify-end">
          <Button loading={isStreaming}>
            <Send className="h-4 w-4" />
            Ask
          </Button>
        </div>
      </form>
    </Panel>
  );
}
