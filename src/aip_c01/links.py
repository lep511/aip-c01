"""Extraction of the hyperlinks referenced by an HTML page.

Links are read from the raw HTML (not from the generated Markdown), resolved to
absolute URLs, deduplicated, and classified as internal or external relative to
the host of the page being converted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

# Tags whose `href` points to another document. `area` belongs to image maps
# and behaves like an anchor.
LINK_TAGS = ("a", "area")

# Only real web links are reported; mailto:, tel:, javascript: and data: URIs
# are not other websites.
ALLOWED_SCHEMES = ("http", "https")

# Fallback shown when an anchor has no usable text (for instance image links).
EMPTY_TEXT_PLACEHOLDER = "(no text)"

# Link labels are trimmed so the generated list stays readable.
MAX_TEXT_LENGTH = 120


@dataclass(frozen=True)
class Link:
    """A single hyperlink found in the page."""

    url: str
    text: str
    is_external: bool


def _clean_text(value: str) -> str:
    """Collapse whitespace and cap the length of an anchor label."""
    text = re.sub(r"\s+", " ", value or "").strip()
    if len(text) > MAX_TEXT_LENGTH:
        text = f"{text[: MAX_TEXT_LENGTH - 1].rstrip()}…"
    return text


def _label_for(element: object) -> str:
    """Best available label for an anchor: its text, its title, or an image alt."""
    text = _clean_text(element.get_text(" ", strip=True))  # type: ignore[attr-defined]
    if text:
        return text

    title = _clean_text(str(element.get("title") or ""))  # type: ignore[attr-defined]
    if title:
        return title

    image = element.find("img")  # type: ignore[attr-defined]
    if image is not None:
        alt = _clean_text(str(image.get("alt") or ""))
        if alt:
            return alt

    return EMPTY_TEXT_PLACEHOLDER


def _absolute_url(base_url: str, href: str) -> str | None:
    """Resolve `href` against `base_url`.

    Returns None when the value is not an http(s) link (anchors to the current
    page without a path, mailto addresses, javascript handlers, ...). The
    fragment is dropped so that several anchors of the same document collapse
    into a single entry.
    """
    href = (href or "").strip()
    if not href or href.startswith("#"):
        return None

    parsed = urlparse(urljoin(base_url, href))
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        return None

    return urlunparse(parsed._replace(fragment=""))


def _same_site(page_host: str, link_host: str) -> bool:
    """Compare hosts ignoring case and a leading `www.`."""
    normalize = lambda host: host.lower().removeprefix("www.")  # noqa: E731
    return normalize(page_host) == normalize(link_host)


def extract_links(html: str, page_url: str) -> list[Link]:
    """Return the http(s) links referenced by `html`, in document order.

    Relative hrefs are resolved against the `<base href>` of the document when
    present, and against `page_url` otherwise. Duplicated URLs are reported
    once, keeping the first label found for them.
    """
    soup = BeautifulSoup(html, "html.parser")

    base_url = page_url
    base_tag = soup.find("base", href=True)
    if base_tag is not None:
        base_url = urljoin(page_url, str(base_tag["href"]).strip())

    page_host = urlparse(page_url).netloc

    links: list[Link] = []
    seen: set[str] = set()
    for element in soup.find_all(LINK_TAGS, href=True):
        url = _absolute_url(base_url, str(element["href"]))
        if url is None or url in seen:
            continue
        seen.add(url)
        links.append(
            Link(
                url=url,
                text=_label_for(element),
                is_external=not _same_site(page_host, urlparse(url).netloc),
            )
        )
    return links


def filter_links(links: list[Link], scope: str) -> list[Link]:
    """Keep the links matching `scope`: `all`, `external`, or `internal`."""
    if scope == "external":
        return [link for link in links if link.is_external]
    if scope == "internal":
        return [link for link in links if not link.is_external]
    return links


def _escape_label(text: str) -> str:
    """Escape the characters that would break a Markdown link label."""
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _render_group(
    title: str, links: list[Link], notes: dict[str, str] | None = None
) -> list[str]:
    """Render one section of the report as Markdown lines."""
    lines = [f"## {title} ({len(links)})", ""]
    if not links:
        lines += ["None found.", ""]
        return lines

    for index, link in enumerate(links, start=1):
        # Angle brackets keep URLs with spaces or parentheses valid in Markdown.
        target = f"<{link.url}>" if re.search(r"[\s()]", link.url) else link.url
        lines.append(f"{index}. [{_escape_label(link.text)}]({target})")
        note = (notes or {}).get(link.url)
        if note:
            # Indented so the note stays inside its numbered item.
            lines.append(f"   - {note}")
    lines.append("")
    return lines


def render_links_markdown(
    page_url: str,
    links: list[Link],
    scope: str,
    notes: dict[str, str] | None = None,
    follow_summary: str | None = None,
) -> str:
    """Build the Markdown report listing the links of a page.

    Args:
        page_url: address the links were taken from.
        links: links to report, already filtered by scope.
        scope: scope that was applied, shown in the summary.
        notes: optional text to show under a link, keyed by URL. Used to point
            to the file where the content of that link was saved.
        follow_summary: optional extra line for the summary block.
    """
    external = [link for link in links if link.is_external]
    internal = [link for link in links if not link.is_external]

    lines = [
        f"# Links found in {page_url}",
        "",
        f"- Source: <{page_url}>",
        f"- Scope: {scope}",
        f"- Total: {len(links)} ({len(external)} external, {len(internal)} internal)",
    ]
    if follow_summary:
        lines.append(f"- {follow_summary}")
    lines.append("")

    # Sections are only emitted for the scopes the user asked for.
    if scope in ("all", "external"):
        lines += _render_group("External links", external, notes)
    if scope in ("all", "internal"):
        lines += _render_group("Internal links", internal, notes)

    return "\n".join(lines).rstrip() + "\n"
