# Productivity Tools

Pre-installed Linux utilities that let Claude Code — or any local LLM / future AI —
**produce and process documents end-to-end**, directly inside the AI Agent Lab, with **no
external cloud service**. These are model-agnostic infrastructure utilities: the same tools
serve any AI with system access.

## Documents

| Tool | Commands | Purpose |
|------|----------|---------|
| **Pandoc** | `pandoc` | Convert documents between Markdown, HTML, LaTeX, DOCX, EPUB, and PDF |
| **TeX Live** | `pdflatex`, `xelatex`, `lualatex` | LaTeX engines — the backend Pandoc uses to render high-quality PDF |
| **Poppler** | `pdftotext`, `pdftoppm`, `pdfinfo` | Extract text from PDFs, render pages to images, inspect PDF metadata |

```bash
pandoc report.md -o report.pdf        # Markdown → PDF (via LaTeX)
pandoc report.md -o report.docx       # Markdown → Word
pandoc document.md -o document.html --css style.css   # Markdown → styled HTML
pdftotext input.pdf output.txt        # PDF → plain text
```

## Installation

These tools are installed in the stack's `docker/vscode/Dockerfile` and available in every
Code-Server terminal — self-contained, fast, and cloud-free.
