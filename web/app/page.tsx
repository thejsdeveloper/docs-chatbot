"use client";

import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ChatHeader } from "@/components/chat/chat-header";
import { EmptyState } from "@/components/chat/empty-state";
import { MessageList } from "@/components/chat/message-list";
import { useChat } from "@/lib/use-chat";

export default function Home() {
  const { messages, isStreaming, sendMessage, retry, stop, reset } = useChat();
  const hasMessages = messages.length > 0;

  const submit = (text: string) => {
    if (!text.trim()) return;
    sendMessage(text);
  };

  return (
    <div className="mx-auto flex h-dvh w-full max-w-3xl flex-col px-4">
      <ChatHeader onReset={reset} showReset={hasMessages} />

      <Conversation className="flex-1 scrollbar-thin">
        <ConversationContent>
          {hasMessages ? (
            <MessageList messages={messages} onRetry={retry} />
          ) : (
            <EmptyState onSelectPrompt={submit} />
          )}
        </ConversationContent>
        <ConversationScrollButton />
      </Conversation>

      <ChatComposer
        isStreaming={isStreaming}
        onStop={stop}
        onSubmit={submit}
      />
      <p className="pt-2 text-center text-muted-foreground text-xs">
        React Docs Chatbot can make mistakes. Check sources for important info.
      </p>
    </div>
  );
}
