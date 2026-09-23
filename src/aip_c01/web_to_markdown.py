"""Convert a website into a Markdown file stored in a separate output directory.

The user provides a URL (as a command line argument or interactively) and the
page is downloaded and converted with MarkItDown. The resulting `.md` file is
written into its own output directory, which is created when missing, together
with a `.links.md` report listing every link the page references.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse, urlunparse

import requests
from markitdown import MarkItDown, MarkItDownException

from aip_c01.links import Link, extract_links, filter_links, render_links_markdown

# Directory (relative to the current working directory) where the generated
# Markdown files are written when the user does not choose another one.
DEFAULT_OUTPUT_DIR = "markdown_output"

# Seconds to wait for the remote server before giving up. MarkItDown does not
# set a timeout on its own, so a hung server would block the program forever.
REQUEST_TIMEOUT = 30

# Upper bound for the generated file name (without extension). Keeps the final
# path comfortably inside the limits of every common filesystem.
MAX_STEM_LENGTH = 100

# Header sent by MarkItDown's own session: ask for Markdown when the server can
# provide it, and fall back to HTML/plain text otherwise.
ACCEPT_HEADER = "text/markdown, text/html;q=0.9, text/plain;q=0.8, */*;q=0.1"

# Several sites reject the default `python-requests` agent with a 403, so the
# request is announced as a regular desktop browser.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


# Error messages are trimmed before they reach the report, because some of them
# (missing MarkItDown extras, for instance) span several lines.
MAX_ERROR_LENGTH = 200


@dataclass
class PageResult:
    """Outcome of converting one of the linked pages."""

    link: Link
    # File written for the linked page, or None when it could not be converted.
    path: Path | None = None
    # Reason of the failure, when `path` is None.
    error: str | None = None

    @property
    def ok(self) -> bool:
        """True when the linked page was converted and written."""
        return self.path is not None


@dataclass
class ConversionResult:
    """Outcome of converting a page and, optionally, the pages it links to."""

    # Markdown file written for the requested page.
    markdown_path: Path
    # Report with the links of the page, or None when it was not generated.
    links_path: Path | None = None
    # Links kept after applying the requested scope.
    links: list[Link] = field(default_factory=list)
    # Reason why no link was collected, when links were requested.
    links_note: str | None = None
    # Directory holding the Markdown of the linked pages, when they were followed.
    pages_dir: Path | None = None
    # One entry per followed link.
    pages: list[PageResult] = field(default_factory=list)

    @property
    def external_count(self) -> int:
        """Number of reported links pointing to another site."""
        return sum(1 for link in self.links if link.is_external)

    @property
    def saved_pages(self) -> int:
        """Number of linked pages that were converted."""
        return sum(1 for page in self.pages if page.ok)

    @property
    def failed_pages(self) -> int:
        """Number of linked pages that could not be converted."""
        return len(self.pages) - self.saved_pages


class TimeoutSession(requests.Session):
    """Requests session that applies a default timeout to every request."""

    def request(self, *args: Any, **kwargs: Any) -> requests.Response:
        # Only fill in the timeout when the caller did not provide one.
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        return super().request(*args, **kwargs)


def build_session() -> requests.Session:
    """Create the HTTP session used to download the website."""
    session = TimeoutSession()
    session.headers.update({"Accept": ACCEPT_HEADER, "User-Agent": USER_AGENT})
    return session


def normalize_url(raw_url: str) -> str:
    """Return a usable http(s) URL from whatever the user typed.

    Surrounding whitespace and quotes are removed and a missing scheme defaults
    to https, so plain input such as `example.com` also works.

    Raises:
        ValueError: when the value is empty or is not an http(s) address.
    """
    url = (raw_url or "").strip().strip("\"'")
    if not url:
        raise ValueError("no URL was provided")

    parsed = urlparse(url)
    if not parsed.scheme:
        # Without a scheme urlparse puts everything in `path`, so re-parse it.
        parsed = urlparse(f"https://{url}")

    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"unsupported scheme '{parsed.scheme}', use http or https")
    if not parsed.netloc:
        raise ValueError(f"'{url}' does not contain a host name")

    return urlunparse(parsed)


def build_file_stem(url: str, *, omit_host: str | None = None) -> str:
    """Derive a filesystem-safe file name (without extension) from the URL.

    Args:
        url: address the name is built from.
        omit_host: host to leave out of the name when it matches the URL. Used
            for the linked pages of a site, whose files would otherwise repeat
            the host of their parent page and grow the path for nothing.
    """
    parsed = urlparse(url)
    host = "" if parsed.netloc.lower() == (omit_host or "").lower() else parsed.netloc
    # Host plus path keeps the name readable and unique enough per page.
    stem = re.sub(r"[^A-Za-z0-9]+", "-", f"{host}{parsed.path}")
    stem = stem.strip("-").lower()[:MAX_STEM_LENGTH].strip("-")
    return stem or "page"


def resolve_output_path(output_dir: Path, stem: str) -> Path:
    """Return a free `.md` path inside `output_dir`.

    Existing conversions are never overwritten: a numeric suffix is appended
    until an unused name is found.
    """
    candidate = output_dir / f"{stem}.md"
    counter = 2
    while candidate.exists():
        candidate = output_dir / f"{stem}-{counter}.md"
        counter += 1
    return candidate


def content_type_of(response: requests.Response) -> str:
    """Return the bare content type of a response, without parameters."""
    return response.headers.get("content-type", "").split(";")[0].strip().lower()


def is_html(response: requests.Response) -> bool:
    """Tell whether the response body is HTML and can be scanned for links."""
    return content_type_of(response) in ("text/html", "application/xhtml+xml")


def fetch_html(session: requests.Session, url: str) -> str | None:
    """Request the HTML representation of `url`, ignoring the default Accept.

    Some sites (AWS documentation among them) answer `text/markdown` to the
    header MarkItDown prefers. That is great for the conversion but carries no
    `<a>` tags, so the HTML version is requested separately for the links.

    Returns:
        The HTML body, or None when the server has no HTML representation.
    """
    response = session.get(
        url, headers={"Accept": "text/html, application/xhtml+xml;q=0.9"}
    )
    response.raise_for_status()
    return response.text if is_html(response) else None


def negotiate_html(
    session: requests.Session, url: str, response: requests.Response
) -> tuple[str | None, str | None]:
    """Try to obtain the HTML of `url` after a non-HTML `response`.

    Returns:
        A `(html, note)` pair. `html` is None when no HTML could be obtained,
        and `note` then explains why.
    """
    # Binary documents (PDF, DOCX, ...) have no HTML version to negotiate; only
    # text formats are worth a second attempt.
    if content_type_of(response).startswith("text/"):
        try:
            html = fetch_html(session, url)
        except requests.RequestException as error:
            return None, f"the HTML version could not be downloaded ({error})"
        if html is not None:
            return html, None

    return None, (
        f"the URL returned {content_type_of(response) or 'no content type'}, "
        "not an HTML document"
    )


def write_text_file(destination: Path, content: str) -> None:
    """Write UTF-8 text with LF endings so output looks the same everywhere."""
    destination.write_text(content, encoding="utf-8", newline="\n")


def summarize_error(error: Exception) -> str:
    """Turn an exception into a single short line suitable for the report."""
    message = re.sub(r"\s+", " ", str(error)).strip() or error.__class__.__name__
    if len(message) > MAX_ERROR_LENGTH:
        message = f"{message[: MAX_ERROR_LENGTH - 1].rstrip()}…"
    return message


def convert_page(
    session: requests.Session,
    converter: MarkItDown,
    url: str,
    directory: Path,
    omit_host: str | None = None,
) -> Path:
    """Download a single page and write its Markdown inside `directory`.

    Returns:
        The path of the file that was written.

    Raises:
        RuntimeError: when the document carries no text.
    """
    response = session.get(url)
    response.raise_for_status()

    markdown = converter.convert_response(response).markdown.strip()
    if not markdown:
        raise RuntimeError("the document has no text content")

    destination = resolve_output_path(
        directory, build_file_stem(url, omit_host=omit_host)
    )
    write_text_file(destination, f"{markdown}\n")
    return destination


def convert_linked_pages(
    session: requests.Session,
    converter: MarkItDown,
    links: Sequence[Link],
    directory: Path,
    omit_host: str | None = None,
    progress: Callable[[int, int, PageResult], None] | None = None,
) -> list[PageResult]:
    """Convert every link into its own Markdown file inside `directory`.

    One failing link does not stop the run: the error is recorded in its
    `PageResult` and the iteration continues with the next link.

    Args:
        session: HTTP session reused for every download.
        converter: MarkItDown instance reused for every conversion.
        links: links to follow, in report order.
        directory: destination directory, created when missing.
        omit_host: host left out of the generated file names.
        progress: optional callback invoked after each link with the position,
            the total, and the result.
    """
    directory.mkdir(parents=True, exist_ok=True)

    results: list[PageResult] = []
    for index, link in enumerate(links, start=1):
        try:
            path = convert_page(session, converter, link.url, directory, omit_host)
            result = PageResult(link=link, path=path)
        except (
            requests.RequestException,
            MarkItDownException,
            RuntimeError,
            ValueError,
            OSError,
        ) as error:
            result = PageResult(link=link, error=summarize_error(error))

        results.append(result)
        if progress is not None:
            progress(index, len(links), result)
    return results


def build_page_notes(pages: Sequence[PageResult], report_dir: Path) -> dict[str, str]:
    """Map every followed URL to the note shown under it in the links report."""
    notes: dict[str, str] = {}
    for page in pages:
        if page.path is None:
            notes[page.link.url] = f"Not saved: {page.error}"
            continue
        # Relative POSIX paths keep the report links working on every platform,
        # and the file name alone keeps the label readable.
        target = page.path.relative_to(report_dir).as_posix()
        notes[page.link.url] = f"Content saved to [{page.path.name}]({target})"
    return notes


def convert_website(
    url: str,
    output_dir: Path,
    *,
    extract_page_links: bool = True,
    links_scope: str = "all",
    follow_links: bool = False,
    max_pages: int = 0,
    progress: Callable[[int, int, PageResult], None] | None = None,
) -> ConversionResult:
    """Download `url`, convert it to Markdown and save it inside `output_dir`.

    The requested page needs a single request: the same response feeds the
    Markdown conversion and the link extraction. A second request is only made
    when the server answered a non-HTML text format and the links were needed.
    With `follow_links`, every link is then downloaded and converted into its
    own file inside a `<name>-pages` subdirectory.

    Args:
        url: http(s) address to convert.
        output_dir: directory that receives the generated files.
        extract_page_links: write the report with the links of the page.
        links_scope: which links to keep: `all`, `external`, or `internal`.
        follow_links: also convert the content of every kept link.
        max_pages: maximum number of links to follow, 0 for no limit.
        progress: callback invoked after each followed link.

    Returns:
        A `ConversionResult` with the files written, the links found, and the
        outcome of every followed link.

    Raises:
        RuntimeError: when the requested page carries no text.
    """
    session = build_session()
    response = session.get(url)
    response.raise_for_status()

    # Read the body before the converter consumes the response, so the HTML is
    # already available for the link extraction without a second request.
    html = response.text if is_html(response) else None
    # `response.url` is the final address after redirects: the correct base for
    # resolving relative links.
    page_url = response.url

    converter = MarkItDown(enable_plugins=False, requests_session=session)
    markdown = converter.convert_response(response).markdown.strip()
    if not markdown:
        raise RuntimeError("the document has no text content")

    # Create the separate output directory on demand, parents included.
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = resolve_output_path(output_dir, build_file_stem(url))
    write_text_file(markdown_path, f"{markdown}\n")

    result = ConversionResult(markdown_path=markdown_path)
    # The links are needed both for the report and for following them.
    if not (extract_page_links or follow_links):
        return result

    if html is None:
        html, result.links_note = negotiate_html(session, url, response)
    if html is None:
        return result

    result.links = filter_links(extract_links(html, page_url), links_scope)

    if follow_links and result.links:
        followed = result.links[:max_pages] if max_pages > 0 else result.links
        # Linked pages live in their own subdirectory, named after the page they
        # were reached from.
        result.pages_dir = markdown_path.with_name(f"{markdown_path.stem}-pages")
        result.pages = convert_linked_pages(
            session,
            converter,
            followed,
            result.pages_dir,
            omit_host=urlparse(page_url).netloc,
            progress=progress,
        )

    if extract_page_links:
        summary = None
        if result.pages:
            summary = (
                f"Content extracted: {result.saved_pages} saved, "
                f"{result.failed_pages} failed, out of {len(result.links)} link(s)"
            )
        # Keep the report beside its page, sharing the same numbered stem.
        result.links_path = markdown_path.with_name(f"{markdown_path.stem}.links.md")
        write_text_file(
            result.links_path,
            render_links_markdown(
                page_url,
                result.links,
                links_scope,
                notes=build_page_notes(result.pages, output_dir),
                follow_summary=summary,
            ),
        )
    return result


def ask_for_url() -> str:
    """Ask the user for a website until a non-empty value is entered."""
    while True:
        try:
            answer = input("Website URL to convert to Markdown: ").strip()
        except EOFError:
            # Non-interactive stdin: nothing else can be read.
            return ""
        if answer:
            return answer
        print("Please enter a URL, or press Ctrl+C to quit.")


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        prog="aip-c01",
        description="Convert a website to a Markdown file using MarkItDown.",
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="website to convert; asked interactively when omitted",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"directory for the generated Markdown (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "-s",
        "--links-scope",
        choices=("all", "external", "internal"),
        default="all",
        help="which links to report (default: all)",
    )
    parser.add_argument(
        "-f",
        "--follow-links",
        dest="follow_links",
        action="store_true",
        help="also convert the content of every link into its own file",
    )
    parser.add_argument(
        "-m",
        "--max-pages",
        type=int,
        default=0,
        metavar="N",
        help="stop after following N links (default: 0, no limit)",
    )
    parser.add_argument(
        "--no-links",
        dest="extract_links",
        action="store_false",
        help="do not generate the .links.md report",
    )
    return parser.parse_args(argv)


def report_page(index: int, total: int, page: PageResult) -> None:
    """Print the outcome of a followed link as it is processed."""
    if index == 1:
        print(f"Extracting the content of {total} link(s):")

    position = f"[{index}/{total}]"
    if page.path is not None:
        print(f"  {position} {page.link.url} -> {page.path.name}")
    else:
        print(f"  {position} {page.link.url} -> failed: {page.error}")


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    args = parse_args(argv)

    try:
        raw_url = args.url or ask_for_url()
        url = normalize_url(raw_url)
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
    except ValueError as error:
        print(f"Invalid input: {error}.", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    print(f"Converting {url} ...")

    try:
        result = convert_website(
            url,
            output_dir,
            extract_page_links=args.extract_links,
            links_scope=args.links_scope,
            follow_links=args.follow_links,
            max_pages=max(args.max_pages, 0),
            progress=report_page if args.follow_links else None,
        )
    except requests.RequestException as error:
        print(f"Download failed: {error}", file=sys.stderr)
        return 1
    except (MarkItDownException, RuntimeError) as error:
        print(f"Conversion failed: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Could not write the Markdown file: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130

    print(f"Saved: {result.markdown_path}")
    if result.links_note is not None:
        print(f"Links: skipped, {result.links_note}.")
        return 0

    print(f"Links: {len(result.links)} found ({result.external_count} to other sites)")
    if result.links_path is not None:
        print(f"Report: {result.links_path}")
    if result.pages_dir is not None:
        print(
            f"Pages: {result.saved_pages} saved, {result.failed_pages} failed "
            f"-> {result.pages_dir}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
