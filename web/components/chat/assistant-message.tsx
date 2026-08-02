import { SparkleIcon } from "lucide-react";
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/components/ai-elements/message";
import { AssistantSources } from "@/components/chat/assistant-sources";
import { Button } from "@/components/ui/button";
import type { ChatMessage } from "@/lib/use-chat";

export function AssistantMessage({
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
