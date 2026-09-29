import { Activity, Database, Gauge, Globe2, MessageSquareText } from "lucide-react";
import { Panel } from "@/components/ui/panel";
import type { Dashboard } from "@/types";

const icons = [Database, MessageSquareText, Gauge, Globe2];

export function DashboardCards({ dashboard }: { dashboard: Dashboard | null }) {
  const cards = [
    ["Documents", dashboard?.total_documents ?? 0],
    ["Chats", dashboard?.total_chats ?? 0],
    ["Retrieval", `${Math.round((dashboard?.average_retrieval_score ?? 0) * 100)}%`],
    ["Web Usage", `${dashboard?.web_search_usage_percent ?? 0}%`]
  ] as const;

  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      {cards.map(([label, value], index) => {
        const Icon = icons[index] ?? Activity;
        return (
          <Panel key={label} className="p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase text-muted">{label}</p>
                <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
              </div>
              <div className="grid h-10 w-10 place-items-center rounded-card border border-border bg-white/[0.04] text-blue-100">
                <Icon className="h-5 w-5" />
              </div>
            </div>
          </Panel>
        );
      })}
    </div>
  );
}
