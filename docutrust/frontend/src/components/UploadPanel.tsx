import { ChangeEvent, useRef, useState } from "react";
import { FileUp, Loader2, UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";

type UploadPanelProps = {
  onUpload: (files: FileList) => Promise<void>;
};

export function UploadPanel({ onUpload }: UploadPanelProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleFiles(event: ChangeEvent<HTMLInputElement>) {
    if (!event.target.files?.length) {
      return;
    }
    setLoading(true);
    try {
      await onUpload(event.target.files);
      event.target.value = "";
    } finally {
      setLoading(false);
    }
  }

  return (
    <Panel className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">PDF Upload</h2>
        <FileUp className="h-4 w-4 text-muted" />
      </div>
      <button
        type="button"
        className="upload-zone group"
        onClick={() => inputRef.current?.click()}
      >
        <span className="grid h-11 w-11 place-items-center rounded-card border border-primary/40 bg-primary/15 text-blue-100">
          {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <UploadCloud className="h-5 w-5" />}
        </span>
        <span className="text-sm font-medium text-white">Attach PDFs</span>
      </button>
      <input ref={inputRef} className="hidden" type="file" accept="application/pdf" multiple onChange={handleFiles} />
      <Button className="mt-3 w-full" variant="secondary" loading={loading} onClick={() => inputRef.current?.click()}>
        Select Files
      </Button>
    </Panel>
  );
}
