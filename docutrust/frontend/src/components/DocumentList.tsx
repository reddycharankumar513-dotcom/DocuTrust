import { FileText, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";
import type { DocumentRecord } from "@/types";

type DocumentListProps = {
  documents: DocumentRecord[];
  onDelete: (id: string) => void;
};

export function DocumentList({ documents, onDelete }: DocumentListProps) {
  return (
    <Panel className="min-h-0 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">Documents</h2>
        <Badge tone="blue">{documents.length}</Badge>
      </div>
      <div className="space-y-2 overflow-y-auto pr-1 lg:max-h-64">
        {documents.map((document) => (
          <div key={document.id} className="row-item">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-card border border-border bg-white/[0.04] text-blue-100">
              <FileText className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-white">{document.filename}</p>
              <p className="text-xs text-muted">{document.chunks_count} chunks</p>
            </div>
            <Badge tone={document.status === "ready" ? "teal" : document.status === "failed" ? "red" : "amber"}>
              {document.status}
            </Badge>
            <Button aria-label="Delete document" title="Delete document" size="icon" variant="ghost" onClick={() => onDelete(document.id)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
        {!documents.length ? <p className="empty-state">No documents</p> : null}
      </div>
    </Panel>
  );
}
