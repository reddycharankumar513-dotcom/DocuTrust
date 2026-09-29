import { CheckCircle2, CircleDot, Loader2, Search, Sparkles, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import type { AgentLog } from "@/types";

const stepIcons = {
  "Query Node": CircleDot,
  "Retriever Node": Search,
  "Grading Node": CheckCircle2,
  "Query Rewriter": Sparkles,
  "Web Search Agent": Search,
  "Answer Generator": Sparkles,
  "Citation Agent": CheckCircle2,
  Workflow: CheckCircle2
};

export function AgentTimeline({ logs, connected }: { logs: AgentLog[]; connected: boolean }) {
  return (
    <Panel className="p-4">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">Agent Logs</h2>
        <Badge tone={connected ? "teal" : "amber"}>{connected ? "Live" : "REST"}</Badge>
      </div>
      <div className="space-y-3">
        {logs.map((log, index) => {
          const Icon = stepIcons[log.step as keyof typeof stepIcons] ?? CircleDot;
          const running = log.status === "running";
          const warning = log.status === "warning" || log.status === "error";
          return (
            <div key={`${log.timestamp}-${index}`} className="timeline-item">
              <span className={warning ? "timeline-icon warning" : "timeline-icon"}>
                {running ? <Loader2 className="h-4 w-4 animate-spin" /> : warning ? <TriangleAlert className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
              </span>
              <span className="min-w-0">
                <span className="block text-sm font-medium text-white">{log.step}</span>
                <span className="block truncate text-xs text-muted">{log.message}</span>
              </span>
            </div>
          );
        })}
        {!logs.length ? <p className="empty-state">Idle</p> : null}
      </div>
    </Panel>
  );
}
