"use client";

import { AnimatePresence, motion } from "motion/react";
import { AssistantMessage } from "@/components/chat/assistant-message";
import { UserMessage } from "@/components/chat/user-message";
import type { ChatMessage } from "@/lib/use-chat";

export function MessageList({
  messages,
  onRetry,
}: {
  messages: ChatMessage[];
  onRetry: () => void;
}) {
  return (
    <AnimatePresence initial={false}>
      {messages.map((message) => (
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          initial={{ opacity: 0, y: 8 }}
          key={message.id}
          transition={{ duration: 0.2, ease: "easeOut" }}
        >
          {message.role === "user" ? (
            <UserMessage content={message.content} />
          ) : (
            <AssistantMessage message={message} onRetry={onRetry} />
          )}
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
