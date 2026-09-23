# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Two things live in one repo:

1. **`aip-c01` CLI tool** — a Python CLI that converts a web page to Markdown using MarkItDown, reports every link the page references, and optionally follows those links to extract each one. The code lives in `src/aip_c01/`.
2. **Docsify v5 documentation site** — a static study guide for the AWS Certified Generative AI Developer – Professional (AIP-C01) exam, deployed to Vercel at `aws-aip-c01.vercel.app`. Content is in `study/` (5 exam domains + reports + official-page extracts). The site entry point is `index.html` with `_sidebar.md` for navigation; each domain subdirectory has its own `_sidebar.md`.

The study content was largely built by running the CLI tool and `scripts/mcp_aws_docs.py` against AWS documentation.

## Commands

```bash
# Install dependencies (creates .venv)
uv sync

# Run the CLI interactively
uv run aip-c01

# Run the CLI with a URL
uv run aip-c01 https://docs.aws.amazon.com/...

# Query AWS docs via the MCP documentation server
uv run python scripts/mcp_aws_docs.py search "Bedrock batch inference"
uv run python scripts/mcp_aws_docs.py read <url>
uv run python scripts/mcp_aws_docs.py batch scripts/lotes/<file>.json

# Verify study materials (checks links, code blocks, skill coverage)
uv run python scripts/verify_study_docs.py study
uv run python scripts/verify_study_docs.py study/domain-3 --no-network

# Local preview of the Docsify site (requires vercel CLI or any static server)
# Docsify has no build step — just serve the repo root
```

## Architecture

- **`src/aip_c01/web_to_markdown.py`** — CLI entry point, URL handling, page conversion, link-following orchestration. Key functions: `normalize_url`, `convert_page`, `convert_website`, `main`.
- **`src/aip_c01/links.py`** — HTML link extraction (`extract_links`), scope filtering, Markdown report rendering.
- **`src/aip_c01/__init__.py`** — public API re-exports for library usage.
- **`scripts/mcp_aws_docs.py`** — standalone JSON-RPC 2.0 client that talks to `awslabs.aws-documentation-mcp-server` over stdio. Used for batch-fetching AWS docs into `study/`. Requires `uvx` in PATH (no extra install).
- **`scripts/verify_study_docs.py`** — validates study Markdown files: checks AWS URLs exist, relative links resolve, code block languages follow conventions, skill coverage matches headings, and reference inventories are complete.
- **`scripts/lotes/`** — batch JSON files (inputs) and their output logs for the MCP doc builder.

## Conventions

- Python 3.13+, managed with `uv`. No pip, no requirements.txt.
- The project is written in a mix of Spanish (comments, script UI, variable names in scripts) and English (library API, README).
- Study content Markdown uses Python for code blocks — not `bash` or `powershell`.
- `markdown_output/` is gitignored; generated files stay out of version control.
- The Docsify site has no build step. Vercel serves it as static files via `vercel.json` (SPA rewrite to `index.html`). The `.vercelignore` excludes Python sources, scripts, and dev files from the deployment.

## Deployment

Vercel auto-deploys on push to `main`. No build command, no install command. Output directory is `.` (repo root). The `vercel.json` configures SPA routing, security headers, and caching (immutable for static assets, must-revalidate for study content).
