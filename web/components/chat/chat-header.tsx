import { PlusIcon, SparkleIcon } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

export function ChatHeader({
  onReset,
  showReset,
}: {
  onReset: () => void;
  showReset: boolean;
}) {
  return (
    <header className="flex items-center justify-between border-border border-b py-4">
      <div className="flex items-center gap-2.5">
        <span className="relative flex size-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-[color-mix(in_oklch,var(--primary),var(--accent-cyan)_55%)] shadow-[0_1px_0_0_rgba(255,255,255,0.25)_inset]">
          <SparkleIcon className="size-4 text-primary-foreground" />
        </span>
        <div className="flex flex-col leading-tight">
          <h1 className="font-heading font-semibold text-foreground text-lg">
            React Docs Chatbot
          </h1>
          <span className="flex items-center gap-1.5 text-muted-foreground text-xs">
            <span className="relative flex size-1.5">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-500/60" />
              <span className="relative inline-flex size-1.5 rounded-full bg-emerald-500" />
            </span>
            Connected
          </span>
        </div>
      </div>
      <div className="flex items-center gap-1">
        {showReset && (
          <Button
            aria-label="New chat"
            className="text-muted-foreground"
            onClick={onReset}
            size="sm"
            type="button"
            variant="ghost"
          >
            <PlusIcon className="size-3.5" />
            New chat
          </Button>
        )}
        <ThemeToggle />
      </div>
    </header>
  );
}
