"""Turn react.dev's MDX into plain markdown the chunker can embed.

react.dev is not plain markdown. Three things break naive ingestion:

1. Titles live in YAML frontmatter, not in a `# h1`. 220 of 222 files have no
   h1 at all, so MarkdownHeaderTextSplitter's "title" slot comes back empty and
   chunks lose the one word most queries are about ("useState").
2. Headings carry explicit anchors: `## Reference {/*reference*/}`.
3. Doc-site components (<Note>, <Pitfall>, <Sandpack>) wrap the prose.

Only the last one is tempting to solve with a blanket regex, and that would be
a mistake: 297 distinct capitalised tags appear *inside* code fences, where
they are React examples rather than chrome. Everything here is fence-aware and
works off a closed list of known components.
"""

import re

# Doc-site chrome. The tag is noise; whatever it wraps is usually the caveat or
# gotcha people actually ask about, so we drop the tag and keep the body.
CHROME = [
    "Sandpack",
    "SandpackRSC",
    "SandpackWithHTMLOutput",
    "Intro",
    "Note",
    "Pitfall",
    "DeepDive",
    "Recap",
    "YouWillLearn",
    "LearnMore",
    "Solution",
    "Hint",
    "Challenges",
    "Recipes",
    "Recipe",
    "InlineToc",
    "TerminalBlock",
    "ConsoleBlock",
    "ConsoleBlockMulti",
    "ConsoleLogLine",
    "Diagram",
    "DiagramGroup",
    "Illustration",
    "IllustrationBlock",
    "YouTubeIframe",
    "TeamMember",
    "BlogCard",
    "Math",
    "MathI",
    "Canary",
    "CanaryBadge",
    "Experimental",
    "ExperimentalBadge",
    "Deprecated",
    "Wip",
]

_NAMES = "|".join(CHROME)
# `[^>]*` spans newlines already, which covers the few multi-line attribute lists.
_CHROME_TAG = re.compile(rf"</?(?:{_NAMES})\b[^>]*/?>")
# `<Recipes>` is the one chrome tag whose *attribute* is documentation. Its 24
# titleText values are the corpus's only comparison signposts -- "Reading a
# Promise with use vs fetching in an Effect", "The difference between
# useCallback and declaring a function directly" -- and they are the phrasing
# people actually ask "why X over Y" in. Deleting the tag with the blanket rule
# below threw them away, so recover the value as a heading first.
#
# `###`, not `####`: all 57 headings inside Recipes blocks are `####`, so a
# `####` title would be overwritten by its own first child in the breadcrumb
# rather than nesting above it. The cost is that the handful of trailing
# paragraphs after a `</Recipes>` inherit this title instead of the enclosing
# one -- a less precise breadcrumb, not a wrong one.
_RECIPES_TITLE = re.compile(r'<Recipes\b[^>]*\btitleText="([^"]*)"[^>]*>')
# CodeStep is the one inline component: it wraps mid-sentence text, so deleting
# the element would corrupt the sentence. Keep the inner text.
_CODESTEP = re.compile(r"<CodeStep\b[^>]*>(.*?)</CodeStep>", re.DOTALL)
_ANCHOR = re.compile(r"\s*\{/\*.*?\*/\}")
# Links written for react.dev's own routing: `/learn/x` and `#section` only
# resolve against the site they were authored on. Copied into a chat answer
# they point at our own origin and 404 (or, for `#section`, at nothing at all,
# since the reader isn't on the page the fragment refers to). Keep the label,
# drop the target. Absolute links are left alone -- they still work.
_RELATIVE_LINK = re.compile(r"!?\[([^\]]*)\]\([/#][^)]*\)")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_TITLE = re.compile(r"^title:\s*(.+?)\s*$", re.MULTILINE)
_ANY_KEY = re.compile(r"^[A-Za-z][\w-]*:\s*(.+?)\s*$", re.MULTILINE)
# Fences are >=3 backticks, closed by >=that many with no info string. The
# 4-backtick fence in blog/2024/12/05/react-19.md desyncs a naive ``` matcher.
_FENCE = re.compile(r"^(\s*)(`{3,})(.*)$")
_BLANKS = re.compile(r"\n{3,}")


def _split_frontmatter(text: str) -> tuple[str | None, str]:
    match = _FRONTMATTER.match(text)
    if not match:
        return None, text
    block, rest = match.group(1), text[match.end() :]
    # The DOM component pages key on the tag name (`meta: "<meta>"`) rather
    # than `title`, so fall back to the first key's value.
    found = _TITLE.search(block) or _ANY_KEY.search(block)
    return (found.group(1).strip("\"'") if found else None), rest


def _clean_prose(text: str) -> str:
    text = _CODESTEP.sub(r"\1", text)
    # Before the blanket strip, which would take the title with the tag.
    text = _RECIPES_TITLE.sub(r"\n### \1\n", text)
    text = _CHROME_TAG.sub("", text)
    text = _RELATIVE_LINK.sub(r"\1", text)
    return "\n".join(
        _ANCHOR.sub("", line) if line.startswith("#") else line
        for line in text.split("\n")
    )


def _keep_fence(info: str, in_sandpack: bool) -> bool:
    """react.dev hides scaffolding files from its own readers; so do we."""
    if "hidden" in info.split():
        return False
    # Sandpack CSS is presentation for the live demo, not documentation.
    return not (in_sandpack and info.split()[:1] == ["css"])


def _normalise_info(info: str) -> str:
    """`js src/App.js active` -> `js src/App.js`; `js {2}` -> `js`."""
    info = re.sub(r"\{.*", "", info).strip()
    return " ".join(w for w in info.split() if w not in {"active", "hidden"})


def clean_markdown(text: str) -> str:
    title, body = _split_frontmatter(text)

    out: list[str] = []
    prose: list[str] = []
    fence_indent: str | None = None
    fence_ticks = ""
    fence_kept = True
    sandpack = 0

    def flush() -> None:
        if prose:
            out.append(_clean_prose("\n".join(prose)))
            prose.clear()

    for line in body.split("\n"):
        match = _FENCE.match(line)

        if fence_indent is None:
            if match:
                flush()
                fence_indent, fence_ticks = match.group(1), match.group(2)
                info = match.group(3).strip()
                fence_kept = _keep_fence(info, sandpack > 0)
                if fence_kept:
                    out.append(f"{fence_indent}{fence_ticks}{_normalise_info(info)}")
                continue
            # Track Sandpack depth on the raw line, before chrome is stripped.
            sandpack += len(re.findall(r"<Sandpack\w*\b", line))
            sandpack -= len(re.findall(r"</Sandpack\w*>", line))
            sandpack = max(sandpack, 0)
            prose.append(line)
        else:
            closes = (
                match
                and len(match.group(2)) >= len(fence_ticks)
                and match.group(3).strip() == ""
            )
            if closes:
                if fence_kept:
                    out.append(f"{fence_indent}{fence_ticks}")
                fence_indent = None
            elif fence_kept:
                out.append(line)

    flush()

    cleaned = _BLANKS.sub("\n\n", "\n".join(out)).strip()
    return f"# {title}\n\n{cleaned}" if title else cleaned
