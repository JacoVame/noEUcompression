# Packet — Phase 5 (optional): reconnect to the compression pipeline

Two premises block this packet and are stated at the top of the brief on purpose.
They were found by inspecting the JS prototype on 2026-08-04: `bench.js` exposes
`--file`, `--dimension`, `--projection random|firstD|svd`, `--k` and friends, and
builds its embeddings internally from co-occurrence — there is **no** import path
for external embeddings. Phase 5 is therefore not plumbing, and a session that
treats it as plumbing will either edit the JS (forbidden) or quietly invent a
mapping.

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md and ./README-fase2.md. Current phase: 5 (marked OPTIONAL in the
phase table). Read also, as read-only reference: ../compressionTest.js,
../bench.js, ../docs/en/pipeline.md, ../docs/en/parameters-and-cli.md.

Goal per the phase table: an end-to-end run of the compression pipeline with the
LEARNED embeddings from Phases 3-4, with honest ratio reporting.

TWO PREMISES BLOCK THIS PACKET. Resolve them explicitly, in writing, before any
code. Do not pick silently, and do not proceed if your reading makes the result
meaningless.

Premise 1 — where the end-to-end run lives. The JS prototype has NO import path
for external embeddings: bench.js takes --file/--dimension/--projection and
builds its own co-occurrence embeddings internally. CLAUDE.md forbids editing the
JS companion in phase-2 sessions. Therefore the default reading of this packet is
Python-side: create phase2/compress.py which takes the learned coordinates and
performs the pipeline's own steps (distance -> clustering -> vocabulary-to-
cluster encoding -> size accounting), using ../compressionTest.js and
../docs/en/pipeline.md as the algorithmic reference to match, not as code to
edit or import. If you conclude the DoD cannot be met without touching the JS,
STOP and report that; only the human PM may unfreeze that scope.

Premise 2 — the signal gap, which is a research step and not plumbing. Phases 2-4
embed WordNet mammal SYNSETS (Route A, English gold hierarchy, 1170 nodes). The
JS pipeline clusters WORDS from a text (Route B, co-occurrence; its demo text is
Italian). Connecting them needs a lemma -> synset mapping, with ambiguity, and a
text whose vocabulary actually intersects the mammal subtree. Locked decision 3
says Route A first, Route B only after, and do not invert. So: fix the corpus
choice explicitly and defend it in one paragraph (an English text with real
mammal vocabulary; ../samples/sample.txt is a 511-byte Italian paragraph and will
not do). State how many vocabulary tokens map to a synset in the subtree and how
many are dropped. If that intersection is too small to carry any claim, STOP and
report the number — a ratio computed on a handful of tokens is not evidence.

Scope guards. eval.py and harness/ frozen since Phase 1. embeddings/euclidean.py
sealed 2026-08-03, embeddings/lorentz.py delivered in Phase 3 — call them, never
edit them. ablation.py partially sealed 2026-08-04: LR_TABLE, the gates and
run_once's scoring path are untouchable; reuse the frozen per-(geometry,
dimension) learning rates from LR_TABLE rather than restating them. The JS
companion in the repo root is read-only. Create only phase2/compress.py.

DoD (binary): ONE command produces the end-to-end result for BOTH geometries at
the same dimension, plus one defensible sentence. Target command:

  python compress.py --dataset wordnet-mammals --dim 2 --seeds 5 --out out/

It must emit, for euclidean and lorentz side by side, mean ± σ across the seed
set: number of clusters, tokens encoded, tokens dropped as unmapped, the size
before and after under an explicitly stated code, and the resulting ratio.

Honesty conditions, which are the point of this phase:
  - The README non-goals bind: NO comparison against gzip, and no claim of "real
    compression". The ratio is the pipeline's own semantic-compression accounting
    (vocabulary collapsed onto cluster ids), and you must write down the code you
    are counting bits under. An unstated code makes the ratio meaningless.
  - Report the lossy side: what the clustering destroys, measured, not asserted.
  - Phase 4 found that the geometry winning on distortion is NOT the one winning
    on reconstruction above d=2 (hyperbolic wins distortion at d=2 and d=10;
    Euclidean takes MAP and mean rank from d=5 on). So "which embedding to
    compress with" is a real choice: report the ratio for both and say which
    metric, if any, predicts the ratio. If neither does, that is the finding.
  - Negative result is a result. If learned embeddings do not beat the JS
    pipeline's own co-occurrence embeddings on its own metric, report it exactly
    as you would a win.

F3 as always: --seed default 20260716, seed sets tagged so the exact set is
identifiable, every artifact in out/, every stated number regenerable by one
printed command, plots (if any) mean ± σ across seeds and never a single seed.

Environment: interpreter from .venv-path, PYTHONSAFEPATH=1, out-of-tree venv (do
not "fix" this — see CLAUDE.md on the nltk CWD-import guard). stdout is cp1252:
printing 'σ' raises UnicodeEncodeError, so keep Unicode in UTF-8 files and plot
titles and fold it to ASCII for the console. Torch is CPU-only by design.

Runtime: the embeddings you need already exist as out/ablation_run_*.json
checkpoints ONLY as metrics, not as coordinates — the Phase-4 driver does not
persist coordinates. Expect to re-train what you need (euclidean wordnet ~430 s
per run, lorentz 500-1100 s) or to persist coordinates as part of this packet's
own artifacts. Say which you chose. Budget accordingly and run in the background.
```
