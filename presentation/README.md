# Presentation

Reveal.js decks for the ~30-minute talk on **HyperbolicTextCompressor**, in Italian (primary) and English.

## Run locally

The decks load reveal.js from a CDN (jsDelivr), so they work out of the box in any modern browser:

```bash
# Italian
xdg-open presentation/it/index.html        # Linux
open    presentation/it/index.html         # macOS
start   presentation/it/index.html         # Windows

# English
xdg-open presentation/en/index.html
```

If your browser blocks loading `slides.md` from a `file://` URL because of CORS, serve the folder via any static server:

```bash
# Python 3
python3 -m http.server -d . 8080
# then visit:
#   http://localhost:8080/presentation/it/
#   http://localhost:8080/presentation/en/
```

## Layout

```
presentation/
├── it/
│   ├── index.html          # Reveal.js entry point (loads slides.md)
│   ├── slides.md           # Markdown source — edit here
│   ├── speaker-notes.md    # Discursive script for the presenter
│   └── deck.pdf            # Optional: print-pdf export (see below)
├── en/
│   ├── index.html
│   ├── slides.md
│   ├── speaker-notes.md
│   └── deck.pdf
└── shared/
    ├── style.css           # Shared theme tweaks
    └── pipeline.svg        # Pipeline asset embedded in slides
```

## Print to PDF

Reveal.js has a built-in print mode. To export `deck.pdf` for either deck:

1. Serve the deck over HTTP (see `python3 -m http.server` above).
2. Open the deck with `?print-pdf` appended:
   - `http://localhost:8080/presentation/it/index.html?print-pdf`
   - `http://localhost:8080/presentation/en/index.html?print-pdf`
3. In your browser print dialog choose **Save as PDF** and **Default** margins. Set the paper size to **A4 landscape**.

### Fully headless (CI-friendly)

```bash
# Linux / macOS, requires Chromium / Google Chrome
PORT=8080
python3 -m http.server -d . $PORT &
HTTP_PID=$!
sleep 1
google-chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf=presentation/it/deck.pdf \
  "http://localhost:${PORT}/presentation/it/index.html?print-pdf"
google-chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf=presentation/en/deck.pdf \
  "http://localhost:${PORT}/presentation/en/index.html?print-pdf"
kill $HTTP_PID
```

The PDFs are not committed by default (see [Why no committed PDF?](#why-no-committed-pdf) below).

## Editing the decks

- Slide content lives entirely in `slides.md`.
- Slide separator: `---` between horizontal slides; `--` (single line) for vertical slides.
- Speaker notes: lines starting with `note:` after a slide.
- Theme: edit `presentation/shared/style.css`.

## Why no committed PDF?

PDF exports of Reveal.js decks rely on a headless Chromium being available at build time. To keep the repository portable and avoid checking in a binary that drifts from the source, we ship the *recipe* rather than the artefact. Run the steps above whenever you need a fresh `deck.pdf`.
