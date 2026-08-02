const REACT_DEV_ORIGIN = "https://react.dev";

/**
 * Map a corpus path back to the page it came from on react.dev.
 *
 * The corpus is a checkout of react.dev's `src/content`, and its routes are
 * the content paths verbatim — so this is just the inverse of the fetch step.
 * We can't link to the file itself: `api/corpus/` is gitignored and never
 * ships, so the public site is the only place the source actually exists.
 *
 *   reference/react/useState.md  ->  https://react.dev/reference/react/useState
 *   learn/index.md               ->  https://react.dev/learn
 *   index.md                     ->  https://react.dev
 */
export function reactDevUrl(source: string): string {
  const path = source.replace(/\.md$/, "").replace(/(^|\/)index$/, "");
  return path ? `${REACT_DEV_ORIGIN}/${path}` : REACT_DEV_ORIGIN;
}

/** `reference/react/useState.md` -> `reference/react/useState` */
export function sourceLabel(source: string): string {
  return source.replace(/\.md$/, "");
}
