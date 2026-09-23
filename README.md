# aip-c01

Command line tool that takes a website URL and saves it as a Markdown file in a
separate output directory, using [MarkItDown](https://github.com/microsoft/markitdown)
for the conversion. It also reports every link the page references and, on
request, iterates over those links and extracts the content of each one into its
own file.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Setup

From the repository root:

```powershell
uv sync
```

This creates the `.venv` environment and installs `markitdown[pdf]`, `requests`,
and `beautifulsoup4`. The `pdf` extra is included so linked PDFs can also be
converted.

## Usage

Interactive mode asks for the URL:

```powershell
uv run aip-c01
```

```
Website URL to convert to Markdown: example.com
Converting https://example.com ...
Saved: C:\GitHub\aip-c01\markdown_output\example-com.md
Links: 1 found (1 to other sites)
Report: C:\GitHub\aip-c01\markdown_output\example-com.links.md
```

Pass the URL directly:

```powershell
uv run aip-c01 https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html
```

Choose a different output directory:

```powershell
uv run aip-c01 https://example.com --output-dir docs_md
```

Report only the links that leave the site, or skip the report entirely:

```powershell
uv run aip-c01 https://example.com --links-scope external
uv run aip-c01 https://example.com --no-links
```

Extract the content of every link into its own file:

```powershell
uv run aip-c01 https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html --follow-links
```

```
Converting https://docs.aws.amazon.com/.../ai-professional-01.html ...
Extracting the content of 17 link(s):
  [1/17] https://docs.aws.amazon.com/.../ai-professional-01.md -> aws-certification-latest-ai-professional-01-ai-professional-01-md.md
  [2/17] https://docs.aws.amazon.com/pdfs/.../ai-professional-01.pdf -> pdfs-aws-certification-latest-ai-professional-01-ai-professional-01-pdf.md
  ...
  [16/17] https://amazonmr.au1.qualtrics.com/jfe/form/SV_... -> failed: the document has no text content
Saved: ...\markdown_output\docs-aws-amazon-com-...-ai-professional-01-html.md
Links: 17 found (2 to other sites)
Report: ...\markdown_output\docs-aws-amazon-com-...-ai-professional-01-html.links.md
Pages: 15 saved, 2 failed -> ...\markdown_output\docs-aws-amazon-com-...-ai-professional-01-html-pages
```

Combine it with the scope to walk only the pages of the same site, and cap how
many links are followed:

```powershell
uv run aip-c01 <url> --follow-links --links-scope internal
uv run aip-c01 <url> --follow-links --max-pages 5
```

### Options

| Argument | Description |
| --- | --- |
| `url` | Website to convert. Asked interactively when omitted. |
| `-o`, `--output-dir` | Target directory for the generated files. Default: `markdown_output`. |
| `-s`, `--links-scope` | Links to keep: `all` (default), `external`, or `internal`. Applies to the report and to the links that are followed. |
| `-f`, `--follow-links` | Also convert the content of every kept link into its own file. |
| `-m`, `--max-pages` | Stop after following N links. Default: `0`, no limit. |
| `--no-links` | Do not generate the `.links.md` report. |
| `-h`, `--help` | Show the built-in help. |

### Output files

Each run writes, inside the output directory:

| File | Content |
| --- | --- |
| `<name>.md` | The requested page converted to Markdown. |
| `<name>.links.md` | The links found in the page, unless `--no-links` is used. |
| `<name>-pages/` | One Markdown file per followed link, with `--follow-links`. |

```
markdown_output/
├── docs-aws-amazon-com-...-ai-professional-01-html.md
├── docs-aws-amazon-com-...-ai-professional-01-html.links.md
└── docs-aws-amazon-com-...-ai-professional-01-html-pages/
    ├── aws-certification-latest-ai-professional-01-ai-professional-01-domain1-html.md
    ├── pdfs-aws-certification-latest-ai-professional-01-ai-professional-01-pdf.md
    └── ...
```

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Conversion finished and the files were written. |
| `1` | Download, conversion, or write error. |
| `2` | Invalid input (empty URL, missing host, scheme other than http/https). |
| `130` | Cancelled with Ctrl+C. |

## Link extraction

Links come from the `href` of the `<a>` and `<area>` tags of the page, in
document order:

- **Absolute URLs.** Relative hrefs are resolved against the `<base href>` of
  the document when present, and against the final URL of the page (after
  redirects) otherwise. Protocol-relative hrefs such as `//cdn.site/app.js`
  inherit the scheme of the page.
- **Only web links.** `mailto:`, `tel:`, `javascript:`, and `data:` URIs are
  ignored, as are anchors that only carry a fragment (`#section`).
- **One entry per destination.** Fragments are removed before deduplicating, so
  the entries of a table of contents collapse into a single link.
- **External vs internal.** A link is external when its host differs from the
  host of the page. The comparison ignores case and a leading `www.`, so
  `example.com` and `www.example.com` count as the same site, while
  `docs.aws.amazon.com` and `aws.amazon.com` do not.
- **Labels.** The anchor text is used, falling back to the `title` attribute,
  then to the `alt` text of a nested image, then to `(no text)`.

Example report for the AWS exam guide page, run with `--follow-links` so each
entry points to the file holding its content:

```markdown
# Links found in https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html

- Source: <https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html>
- Scope: all
- Total: 17 (2 external, 15 internal)
- Content extracted: 15 saved, 2 failed, out of 17 link(s)

## External links (2)

1. [AWS Certified Generative AI Developer - Professional (AIP-C01)](https://aws.amazon.com/certification/certified-generative-ai-developer-professional/)
   - Content saved to [aws-amazon-com-certification-certified-generative-ai-developer-professional.md](...)
2. [taking our survey](https://amazonmr.au1.qualtrics.com/jfe/form/SV_8vLR1a9uG9zu9Po?course_title=AI-Pro&course_id=AIP-C01&Q_Language=EN)
   - Not saved: the document has no text content

## Internal links (15)

1. [View a markdown version of this page](https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.md)
   - Content saved to [aws-certification-latest-ai-professional-01-ai-professional-01-md.md](...)
...
```

## Following the links

With `--follow-links`, every link kept by `--links-scope` is downloaded and
converted the same way as the requested page:

- **One file per link,** written inside `<name>-pages/`. Names follow the same
  rule as the main page, except that the host is left out when it matches the
  page being crawled, which keeps the names short and readable.
- **Errors do not stop the run.** A link that answers 404, times out, or has no
  text is recorded in the report (`Not saved: ...`) and the iteration continues
  with the next one. The exit code stays `0`: the requested page was converted.
- **Any format MarkItDown can read.** Linked PDFs are converted too, since the
  `pdf` extra is installed. Other formats need their own extras.
- **Depth of one.** Only the links of the requested page are followed; the links
  found inside those pages are not.
- **Same session for everything,** so the connection is reused across the whole
  crawl. There is no rate limiting, so keep `--max-pages` in mind on pages with
  hundreds of links.

## Behaviour

- **URL normalization.** Whitespace and surrounding quotes are stripped, and
  `https://` is added when the scheme is missing, so `example.com` works.
  Anything that is not http/https is rejected before any request is made.
- **Output directory.** Created on demand, including parent directories.
  Relative paths resolve against the current working directory.
- **File names.** Derived from the host and path, lowercased, with every
  non-alphanumeric run replaced by a hyphen and a 100 character cap.
  `https://www.iana.org/help/example-domains` becomes
  `www-iana-org-help-example-domains.md`.
- **No overwrites.** If the target name already exists, a numeric suffix is
  added (`example-com-2.md`, `example-com-3.md`, ...), and the report and the
  page directory follow the same stem (`example-com-2.links.md`,
  `example-com-2-pages/`).
- **HTTP session.** Requests carry a browser `User-Agent`, because several sites
  answer `403` to the default `python-requests` agent, and a 30 second timeout,
  since MarkItDown does not set one and a stalled server would hang the process.
- **One request, usually two for markdown-first sites.** The page is downloaded
  once and the same response feeds the conversion and the link extraction. Some
  sites, AWS documentation included, honour the `text/markdown` preference of
  MarkItDown: that Markdown is cleaner, but it carries no `<a>` tags, so the HTML
  version is requested a second time to collect the links.
- **Line endings.** Files are written as UTF-8 with LF endings.

## Project structure

```
src/aip_c01/
├── __init__.py            # exposes main() for the aip-c01 entry point
├── links.py               # link extraction and report rendering
└── web_to_markdown.py     # CLI, URL handling, and conversion logic
```

Main functions in `web_to_markdown.py`:

| Function | Responsibility |
| --- | --- |
| `normalize_url` | Validates and completes the URL typed by the user. |
| `build_file_stem` | Turns the URL into a filesystem-safe name. |
| `resolve_output_path` | Picks a free `.md` path inside a directory. |
| `negotiate_html` | Asks for the HTML version when the server answered another format. |
| `convert_page` | Downloads one URL and writes its Markdown file. |
| `convert_linked_pages` | Iterates over the links, converting each one. |
| `convert_website` | Orchestrates the page, the report, and the followed links. |
| `main` | Argument parsing, prompting, progress, and error reporting. |

Main functions in `links.py`:

| Function | Responsibility |
| --- | --- |
| `extract_links` | Reads the HTML and returns the `Link` list of the page. |
| `filter_links` | Applies the requested scope. |
| `render_links_markdown` | Builds the Markdown report. |

Both parts can be used as a library:

```python
from pathlib import Path

from aip_c01 import convert_website, extract_links

result = convert_website(
    "https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html",
    Path("markdown_output"),
    links_scope="internal",
    follow_links=True,
    max_pages=5,
)
print(result.markdown_path, result.links_path, result.pages_dir)
print(result.saved_pages, "saved,", result.failed_pages, "failed")
for page in result.pages:
    print(page.link.url, "->", page.path or page.error)

# Or work on HTML you already have.
links = extract_links("<a href='/docs'>Docs</a>", "https://example.com/")
```

## Limitations

- Pages are fetched without running JavaScript, so client-rendered sites may
  produce little or no content, and links injected by scripts are not visible.
- Only one level of links is followed, and only from a single starting URL.
- Formats beyond HTML and PDF depend on the MarkItDown extras, which are not
  installed here. A link to a `.docx`, for instance, is reported as not saved.
- `markdown_output/` is listed in `.gitignore`, so generated files stay out of
  version control.
