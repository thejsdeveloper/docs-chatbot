"use client";

import {
  PromptInput,
  PromptInputBody,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
} from "@/components/ai-elements/prompt-input";

export function ChatComposer({
  isStreaming,
  onStop,
  onSubmit,
}: {
  isStreaming: boolean;
  onStop: () => void;
  onSubmit: (text: string) => void;
}) {
  return (
    <PromptInput
      className="mb-4 rounded-2xl border border-border bg-card shadow-sm"
      onSubmit={(message) => onSubmit(message.text)}
    >
      <PromptInputBody>
        <PromptInputTextarea className="p-4" />
      </PromptInputBody>
      <PromptInputFooter>
        <span />
        <PromptInputSubmit
          onStop={onStop}
          status={isStreaming ? "streaming" : undefined}
        />
      </PromptInputFooter>
    </PromptInput>
  );
}
