import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type BadgeProps = {
  children: ReactNode;
  tone?: "blue" | "teal" | "amber" | "red" | "slate";
  className?: string;
};

export function Badge({ children, tone = "slate", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-medium",
        tone === "blue" && "border-primary/40 bg-primary/15 text-blue-100",
        tone === "teal" && "border-success/40 bg-success/15 text-teal-100",
        tone === "amber" && "border-warning/40 bg-warning/15 text-amber-100",
        tone === "red" && "border-danger/40 bg-danger/15 text-red-100",
        tone === "slate" && "border-border bg-white/[0.05] text-slate-300",
        className
      )}
    >
      {children}
    </span>
  );
}
