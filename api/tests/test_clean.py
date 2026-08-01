from rag.chunker import chunk_markdown
from rag.clean import clean_markdown


def test_frontmatter_title_becomes_h1():
    """react.dev keeps titles in frontmatter; without this the chunker's
    'title' slot is empty and chunks never mention what the page is about."""
    assert clean_markdown("---\ntitle: useState\n---\n\nbody").startswith("# useState")


def test_falls_back_to_first_key_when_no_title():
    """The DOM component pages key on the tag name instead of `title`."""
    assert clean_markdown('---\nmeta: "<meta>"\n---\n\nbody').startswith("# <meta>")


def test_strips_heading_anchors():
    assert clean_markdown("## Reference {/*reference*/}\n") == "## Reference"


def test_drops_chrome_but_keeps_body():
    out = clean_markdown("<Pitfall>\n\nDo not mutate state.\n\n</Pitfall>\n")
    assert "Pitfall" not in out
    assert "Do not mutate state." in out


def test_keeps_jsx_inside_code_fences():
    """297 capitalised tags live inside fences as React examples, not chrome."""
    out = clean_markdown("<Sandpack>\n\n```js\n<Suspense><Note /></Suspense>\n```\n\n</Sandpack>\n")
    assert "<Suspense><Note /></Suspense>" in out
    assert "<Sandpack>" not in out


def test_unwraps_inline_codestep():
    out = clean_markdown("Every <CodeStep step={2}>reactive value</CodeStep> counts.\n")
    assert out == "Every reactive value counts."


def test_drops_hidden_and_sandpack_css_fences():
    out = clean_markdown(
        "<Sandpack>\n\n```json package.json hidden\n{}\n```\n"
        "```css\n.a { color: red }\n```\n"
        "```js src/App.js active\nexport default App;\n```\n\n</Sandpack>\n"
    )
    assert "package.json" not in out and "color: red" not in out
    assert "```js src/App.js" in out  # flags stripped, filename kept


def test_four_backtick_fence_does_not_desync():
    """A ```` fence must not swallow the prose that follows it."""
    out = clean_markdown("````\ncode\n````\n\n## After {/*after*/}\n")
    assert out.endswith("## After") and "{/*" not in out


def test_chunks_carry_the_page_title():
    chunks = chunk_markdown(
        "---\ntitle: useState\n---\n\n## Reference {/*reference*/}\n\n" + "word " * 200
    )
    assert chunks and all(c.startswith("useState > Reference") for c in chunks)
