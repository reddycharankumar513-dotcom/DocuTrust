import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type PanelProps = {
  children: ReactNode;
  className?: string;
};

export function Panel({ children, className }: PanelProps) {
  return <section className={cn("rounded-card border border-border bg-panel shadow-panel", className)}>{children}</section>;
}
