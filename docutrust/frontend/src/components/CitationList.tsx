import { ExternalLink, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Panel } from "@/components/ui/panel";
import type { Source } from "@/types";

export function CitationList({ sources }: { sources: Source[] }) {
  return (
    <Panel className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">Source Citations</h2>
        <Badge tone="blue">{sources.length}</Badge>
      </div>
      <div className="space-y-2">
        {sources.map((source) => {
          const isWeb = /^https?:\/\//.test(source.filename);
          return (
            <div className="source-item" key={source.source_id}>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-blue-100" />
                <p className="min-w-0 flex-1 truncate text-sm font-medium text-white">{source.filename}</p>
                {source.score !== null ? <Badge tone="teal">{Math.round(source.score * 100)}%</Badge> : null}
                {isWeb ? <ExternalLink className="h-4 w-4 text-muted" /> : null}
              </div>
              <p className="mt-1 text-xs text-muted">{source.page ? `Page ${source.page}` : "Reference"}</p>
              <p className="mt-2 line-clamp-3 text-xs leading-5 text-slate-300">{source.snippet}</p>
            </div>
          );
        })}
        {!sources.length ? <p className="empty-state">No citations</p> : null}
      </div>
    </Panel>
  );
}
