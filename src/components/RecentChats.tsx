import { Clock3, MessageSquareText } from "lucide-react";
import { Panel } from "@/components/ui/panel";
import type { ChatResponse } from "@/types";

export function RecentChats({ chats, onSelect }: { chats: ChatResponse[]; onSelect: (chat: ChatResponse) => void }) {
  return (
    <Panel className="min-h-0 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">Recent Chats</h2>
        <Clock3 className="h-4 w-4 text-muted" />
      </div>
      <div className="space-y-2 overflow-y-auto pr-1 lg:max-h-56">
        {chats.slice(0, 8).map((chat) => (
          <button key={chat.id ?? chat.timestamp} className="row-item w-full text-left" type="button" onClick={() => onSelect(chat)}>
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-card border border-border bg-white/[0.04] text-teal-100">
              <MessageSquareText className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-medium text-white">{chat.question}</p>
              <p className="text-xs text-muted">{Math.round(chat.retrieval_score * 100)}% retrieval</p>
            </div>
          </button>
        ))}
        {!chats.length ? <p className="empty-state">No chat history</p> : null}
      </div>
    </Panel>
  );
}
