import { Message, MessageContent } from "@/components/ai-elements/message";

export function UserMessage({ content }: { content: string }) {
  return (
    <Message from="user">
      <MessageContent className="rounded-2xl bg-secondary px-4 py-2.5 text-[0.9375rem] text-secondary-foreground leading-7">
        {content}
      </MessageContent>
    </Message>
  );
}
