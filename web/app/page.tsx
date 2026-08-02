"use client";

import {
  BoxIcon,
  ListIcon,
  PlusIcon,
  RepeatIcon,
  ServerIcon,
  SparkleIcon,
} from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message";
import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
} from "@/components/ai-elements/prompt-input";
import {
  Source,
  Sources,
  SourcesContent,
  SourcesTrigger,
} from "@/components/ai-elements/sources";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { reactDevUrl, sourceLabel } from "@/lib/react-dev-url";
import { useChat, type ChatMessage } from "@/lib/use-chat";

function AssistantSources({ sources }: { sources: ChatMessage["sources"] }) {
  if (!sources || sources.length === 0) return null;

  // Retrieval matches chunks, but this list is about documents: a question
  // aimed squarely at one page ("useSyncExternalStore") can match four
  // passages of it and render the same link four times. Collapse by source.
  // Hits arrive best-first, so first-seen order is also strongest-first.
  const passages = new Map<string, number>();
  for (const hit of sources) {
    passages.set(hit.source, (passages.get(hit.source) ?? 0) + 1);
  }

  return (
    <Sources className="mb-3">
      <SourcesTrigger count={passages.size} />
      <SourcesContent>
        {[...passages].map(([source, count]) => (
          <Source
            href={reactDevUrl(source)}
            key={source}
            title={
              count > 1
                ? `${sourceLabel(source)} · ${count} passages`
                : sourceLabel(source)
            }
          />
        ))}
      </SourcesContent>
    </Sources>
  );
}

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

function AssistantMessage({
  message,
  onRetry,
}: {
  message: ChatMessage;
  onRetry: () => void;
}) {
  return (
    <Message className="max-w-full flex-row items-start gap-3" from="assistant">
      <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
        <SparkleIcon className="size-3.5" />
      </span>
      <MessageContent className="min-w-0 flex-1 px-0 py-0 text-[0.9375rem] leading-7">
        <AssistantSources sources={message.sources} />
        {message.content && (
          <MessageResponse isAnimating={message.status === "streaming"}>
            {message.content}
          </MessageResponse>
        )}
        {message.status === "error" && (
          <div className="flex flex-col gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-destructive text-sm">
            <p>{message.error ?? "Something went wrong."}</p>
            <Button
              className="self-start"
              onClick={onRetry}
              size="sm"
              type="button"
              variant="outline"
            >
              Retry
            </Button>
          </div>
        )}
      </MessageContent>
    </Message>
  );
}

export default function Home() {
  const { messages, isStreaming, sendMessage, retry, stop, reset } = useChat();
  const hasMessages = messages.length > 0;

  const submit = (text: string) => {
    if (!text.trim()) return;
    sendMessage(text);
  };

  return (
    <div className="mx-auto flex h-dvh w-full max-w-3xl flex-col px-4">
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
          {hasMessages && (
            <Button
              aria-label="New chat"
              className="text-muted-foreground"
              onClick={reset}
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

      <Conversation className="flex-1 scrollbar-thin">
        <ConversationContent>
          {hasMessages ? (
            <AnimatePresence initial={false}>
              {messages.map((message) =>
                message.role === "user" ? (
                  <motion.div
                    animate={{ opacity: 1, y: 0 }}
                    initial={{ opacity: 0, y: 8 }}
                    key={message.id}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                  >
                    <Message from="user">
                      <MessageContent className="rounded-2xl bg-secondary px-4 py-2.5 text-[0.9375rem] text-secondary-foreground leading-7">
                        {message.content}
                      </MessageContent>
                    </Message>
                  </motion.div>
                ) : (
                  <motion.div
                    animate={{ opacity: 1, y: 0 }}
                    initial={{ opacity: 0, y: 8 }}
                    key={message.id}
                    transition={{ duration: 0.2, ease: "easeOut" }}
                  >
                    <AssistantMessage message={message} onRetry={retry} />
                  </motion.div>
                ),
              )}
            </AnimatePresence>
          ) : (
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
                    onClick={() => submit(prompt)}
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
          )}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>

      <PromptInput
        className="mb-4 rounded-2xl border border-border bg-card shadow-sm"
        onSubmit={(message) => submit(message.text)}
      >
        <PromptInputBody>
          <PromptInputTextarea className="p-4" />
        </PromptInputBody>
        <PromptInputFooter>
          <span />
          <PromptInputSubmit
            onStop={stop}
            status={isStreaming ? "streaming" : undefined}
          />
        </PromptInputFooter>
      </PromptInput>
      <p className="pt-2 text-center text-muted-foreground text-xs">
        React Docs Chatbot can make mistakes. Check sources for important info.
      </p>
    </div>
  );
}
