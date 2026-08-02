import {
  BoxIcon,
  ListIcon,
  RepeatIcon,
  ServerIcon,
  SparkleIcon,
} from "lucide-react";

const SUGGESTIONS = [
  {
    icon: RepeatIcon,
    label: "Effects running twice",
    prompt: "Why does my Effect run twice on mount?",
  },
  {
    icon: ListIcon,
    label: "Updating array state",
    prompt: "How do I update state in an array?",
  },
  {
    icon: ServerIcon,
    label: "Server Components",
    prompt: "What are Server Components?",
  },
  {
    icon: BoxIcon,
    label: "When to use useRef",
    prompt: "When do I need useRef?",
  },
];

export function EmptyState({
  onSelectPrompt,
}: {
  onSelectPrompt: (prompt: string) => void;
}) {
  return (
    <div className="flex size-full flex-col items-center justify-center gap-8 p-8 text-center">
      <div className="space-y-3">
        <span className="mx-auto flex size-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-[color-mix(in_oklch,var(--primary),var(--accent-cyan)_55%)] shadow-lg shadow-primary/20">
          <SparkleIcon className="size-7 text-primary-foreground" />
        </span>
        <h2 className="font-heading font-semibold text-2xl text-foreground tracking-tight">
          Ask anything about React
        </h2>
        <p className="mx-auto max-w-sm text-muted-foreground text-sm">
          Get instant, sourced answers pulled straight from the React
          documentation.
        </p>
      </div>
      <div className="grid w-full grid-cols-1 gap-2 sm:grid-cols-2">
        {SUGGESTIONS.map(({ icon: Icon, label, prompt }) => (
          <button
            className="group flex items-center gap-2.5 rounded-xl border border-border/80 bg-card/60 px-3.5 py-3 text-left text-sm transition-colors hover:border-primary/40 hover:bg-accent/60"
            key={label}
            onClick={() => onSelectPrompt(prompt)}
            type="button"
          >
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
              <Icon className="size-4" />
            </span>
            <span className="text-foreground">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
