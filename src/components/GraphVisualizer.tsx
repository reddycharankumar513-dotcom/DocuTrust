import { ArrowRight, BrainCircuit, FileSearch, Globe2, PencilLine, ShieldCheck, Sparkles } from "lucide-react";
import { Panel } from "@/components/ui/panel";

const nodes = [
  ["Query", BrainCircuit],
  ["Retrieve", FileSearch],
  ["Grade", ShieldCheck],
  ["Rewrite", PencilLine],
  ["Web", Globe2],
  ["Answer", Sparkles]
] as const;

export function GraphVisualizer({ activeWebFallback }: { activeWebFallback: boolean }) {
  return (
    <Panel className="p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">LangGraph Flow</h2>
        <span className={activeWebFallback ? "status-dot amber" : "status-dot teal"} />
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-6">
        {nodes.map(([label, Icon], index) => (
          <div className="graph-node" key={label}>
            <Icon className="h-4 w-4" />
            <span>{label}</span>
            {index < nodes.length - 1 ? <ArrowRight className="graph-arrow" /> : null}
          </div>
        ))}
      </div>
    </Panel>
  );
}
