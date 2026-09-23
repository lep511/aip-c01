"""Package entry point: expose the website-to-Markdown converter CLI."""

from aip_c01.links import Link, extract_links, filter_links, render_links_markdown
from aip_c01.web_to_markdown import (
    ConversionResult,
    PageResult,
    convert_linked_pages,
    convert_website,
    main,
)

__all__ = [
    "ConversionResult",
    "Link",
    "PageResult",
    "convert_linked_pages",
    "convert_website",
    "extract_links",
    "filter_links",
    "main",
    "render_links_markdown",
]
