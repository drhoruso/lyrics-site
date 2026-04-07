# Lyrics Site

A small static site for bilingual lyrics pages.

Each song page is generated from structured data and shared templates, then published as static HTML for GitHub Pages.

## Structure

- `data/` — song data in JSON
- `templates/` — shared HTML templates
- `scripts/build.py` — site generator
- `<slug>/index.html` — generated public pages
- `index.html` — generated top page

## Requirements

- Python 3
- GNU Make

## Usage

Build everything:

```bash
make build
```

Build one song only:

```bash
make one SONG=and-then
```

Check JSON syntax:

```bash
make check
```

Clean generated files:

```bash
make clean
```

## Notes

- Song-specific content should live in `data/`.
- Shared layout and styling should live in `templates/`.
- Generated HTML is committed so GitHub Pages can publish it directly.
