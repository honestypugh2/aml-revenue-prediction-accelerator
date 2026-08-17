"""Build a static HTML version of the accelerator's Markdown docs.

Converts README.md, docs/**/*.md, and (locally) demo-local/*.md into a browsable
static site under site/ with a sidebar, syntax highlighting, and Mermaid diagram
rendering. Relative .md links are rewritten to .html so the site is navigable
offline (open site/index.html in a browser).

Usage:
    python scripts/build_docs_html.py            # build into ./site
    python scripts/build_docs_html.py --out dist/docs
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parents[1]
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
_MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
_MD_LINK_RE = re.compile(r"\]\((?!https?://|#|mailto:)([^)]+?)\)")


@dataclass(frozen=True)
class Page:
    src: Path  # absolute source markdown path
    rel_out: Path  # output path relative to the site root (e.g. docs/x.html)
    title: str


def _discover_pages() -> list[Page]:
    pages: list[Page] = [Page(REPO_ROOT / "README.md", Path("index.html"), "Home")]
    roots = ["docs"]
    if (REPO_ROOT / "demo-local").is_dir():
        roots.append("demo-local")  # local-only; site/ is git-ignored too
    for root in roots:
        for md in sorted((REPO_ROOT / root).rglob("*.md")):
            rel = md.relative_to(REPO_ROOT)
            out = rel.with_suffix(".html")
            title = _first_heading(md) or md.stem.replace("-", " ").title()
            pages.append(Page(md, out, title))
    return pages


def _first_heading(md_path: Path) -> str | None:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _rewrite_md_links(text: str) -> str:
    """Rewrite relative .md links to .html (preserving any #anchor)."""

    def repl(match: re.Match[str]) -> str:
        target = match.group(1)
        anchor = ""
        if "#" in target:
            target, anchor = target.split("#", 1)
            anchor = "#" + anchor
        if target.endswith(".md"):
            target = target[:-3] + ".html"
        return f"]({target}{anchor})"

    return _MD_LINK_RE.sub(repl, text)


def _extract_mermaid(md_text: str) -> tuple[str, list[str]]:
    """Replace mermaid fences with placeholders; return (text, raw_blocks)."""
    blocks: list[str] = []

    def repl(match: re.Match[str]) -> str:
        blocks.append(match.group(1).strip())
        return f"\n\nMERMAIDPLACEHOLDER{len(blocks) - 1}\n\n"

    return _MERMAID_RE.sub(repl, md_text), blocks


def _restore_mermaid(html_text: str, blocks: list[str]) -> str:
    for i, block in enumerate(blocks):
        placeholder = f"<p>MERMAIDPLACEHOLDER{i}</p>"
        div = f'<pre class="mermaid">{html.escape(block)}</pre>'
        html_text = html_text.replace(placeholder, div)
    return html_text


def _relative_prefix(rel_out: Path) -> str:
    """'' for a root page, '../' per nested level (for nav/asset links)."""
    depth = len(rel_out.parts) - 1
    return "../" * depth


def _nav_html(pages: list[Page], current: Page) -> str:
    prefix = _relative_prefix(current.rel_out)
    groups: dict[str, list[Page]] = {}
    for page in pages:
        if page.rel_out == Path("index.html"):
            continue
        group = page.rel_out.parts[0]
        groups.setdefault(group, []).append(page)

    items = [f'<a class="nav-home" href="{prefix}index.html">Home</a>']
    for group, group_pages in sorted(groups.items()):
        items.append(f'<div class="nav-group">{html.escape(group)}</div>')
        for page in group_pages:
            href = prefix + page.rel_out.as_posix()
            cls = "nav-link active" if page.rel_out == current.rel_out else "nav-link"
            items.append(f'<a class="{cls}" href="{href}">{html.escape(page.title)}</a>')
    return "\n".join(items)


_CSS = """
:root { --bg:#0d1117; --panel:#161b22; --text:#e6edf3; --muted:#8b949e; --accent:#58a6ff; --border:#30363d; }
* { box-sizing: border-box; }
body { margin:0; font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  background:var(--bg); color:var(--text); display:flex; }
aside { width:300px; min-width:300px; height:100vh; overflow-y:auto; position:sticky; top:0;
  background:var(--panel); border-right:1px solid var(--border); padding:16px; }
main { flex:1; max-width:900px; margin:0 auto; padding:32px 40px; overflow-x:auto; }
a { color:var(--accent); text-decoration:none; } a:hover { text-decoration:underline; }
.nav-home { display:block; font-weight:600; margin-bottom:8px; }
.nav-group { color:var(--muted); text-transform:uppercase; font-size:11px; letter-spacing:.05em;
  margin:14px 0 4px; }
.nav-link { display:block; padding:3px 8px; border-radius:6px; font-size:14px; color:var(--text); }
.nav-link:hover { background:#21262d; text-decoration:none; }
.nav-link.active { background:#1f6feb33; color:var(--accent); }
h1,h2,h3 { line-height:1.25; } h1 { border-bottom:1px solid var(--border); padding-bottom:.3em; }
code { background:#161b22; padding:.15em .35em; border-radius:6px; font-size:.9em; }
pre { background:#161b22; border:1px solid var(--border); border-radius:8px; padding:14px; overflow:auto; }
pre code { background:none; padding:0; }
table { border-collapse:collapse; width:100%; margin:1em 0; display:block; overflow-x:auto; }
th,td { border:1px solid var(--border); padding:8px 10px; text-align:left; }
th { background:#161b22; }
blockquote { border-left:3px solid var(--accent); margin:1em 0; padding:.2em 1em; color:var(--muted); }
.mermaid { background:#fff; border-radius:8px; padding:12px; }
"""

_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Revenue Prediction Accelerator docs</title>
<style>{css}</style>
</head>
<body>
<aside>{nav}</aside>
<main>{content}</main>
<script type="module">
import mermaid from "{mermaid_cdn}";
mermaid.initialize({{ startOnLoad: true, theme: "default" }});
</script>
</body>
</html>
"""


def build(out_dir: Path) -> int:
    pages = _discover_pages()
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list", "codehilite"],
        extension_configs={"codehilite": {"noclasses": True, "pygments_style": "friendly"}},
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    for page in pages:
        raw = page.src.read_text(encoding="utf-8")
        raw = _rewrite_md_links(raw)
        raw, mermaid_blocks = _extract_mermaid(raw)
        md.reset()
        body = md.convert(raw)
        body = _restore_mermaid(body, mermaid_blocks)
        document = _TEMPLATE.format(
            title=html.escape(page.title),
            css=_CSS,
            nav=_nav_html(pages, page),
            content=body,
            mermaid_cdn=MERMAID_CDN,
        )
        dest = out_dir / page.rel_out
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(document, encoding="utf-8")
    return len(pages)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="site", help="Output directory (default: site)")
    args = parser.parse_args()
    out_dir = (REPO_ROOT / args.out).resolve()
    count = build(out_dir)
    print(f"Built {count} pages -> {out_dir}")
    print(f"Open: {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
