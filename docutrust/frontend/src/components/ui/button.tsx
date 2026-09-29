import { forwardRef, type ButtonHTMLAttributes } from "react";
import { Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "icon";
  loading?: boolean;
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", loading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-card border text-sm font-medium transition",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/70 disabled:pointer-events-none disabled:opacity-50",
          variant === "primary" && "border-primary bg-primary text-white hover:bg-blue-500",
          variant === "secondary" && "border-border bg-white/[0.06] text-slate-100 hover:bg-white/[0.1]",
          variant === "ghost" && "border-transparent bg-transparent text-muted hover:bg-white/[0.07] hover:text-white",
          variant === "danger" && "border-danger/50 bg-danger/15 text-red-100 hover:bg-danger/25",
          size === "sm" && "h-8 px-3",
          size === "md" && "h-10 px-4",
          size === "icon" && "h-9 w-9 px-0",
          className
        )}
        {...props}
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
