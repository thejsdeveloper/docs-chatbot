import {
  Source,
  Sources,
  SourcesContent,
  SourcesTrigger,
} from "@/components/ai-elements/sources";
import { reactDevUrl, sourceLabel } from "@/lib/react-dev-url";
import type { ChatMessage } from "@/lib/use-chat";

export function AssistantSources({
  sources,
}: {
  sources: ChatMessage["sources"];
}) {
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
