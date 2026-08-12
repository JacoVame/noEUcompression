# Packet — Phase 6 (redefined): the public cantiere note

**What this is.** Phase 6's original DoD ("carta 02 §4 gains a real chart") is
spent — carta 02 was published on 2026-08-05. The slot is reused for the public
closure: a reader-facing note on what Phase 5 actually found, living where the
readers are. The root `README.md` routing half landed in `084ee0c`; this packet
delivers the note itself.

**Scope exception, authorised by the PM on 2026-08-12.** CLAUDE.md places the JS
companion out of scope for phase-2 sessions. For THIS session only, that exception
is narrowed: **prose additions under `docs/it/` and `docs/en/` are authorised** —
two new files and one link line in each of the three READMEs (`docs/it/README.md`,
`docs/en/README.md`, root `README.md`). No `.js` file, no existing doc page, no
HTML, no presentation material. Precedent: Phase 5d edited root `README.md` on the
same terms.

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md, ./README-fase2.md, ./FINDINGS.md and
./packets/phase6-public-note.md (the scope exception is in the packet). Current
phase: 6 (redefined — the public cantiere note).

Deliver two mirrored notes and three links, and nothing else:

  docs/it/cantiere-fase2.md   (Italian, the primary)
  docs/en/phase2-note.md      (English, same content, not a word-by-word
                               translation but the same claims and numbers)

plus one link line in docs/it/README.md, docs/en/README.md and the root
README.md's "Measured results" block.

What the note is. A cantiere (worksite) note: what this repository set out to
measure, what it found, and what it does not claim — for a reader arriving from
the published articles, in plain language, 600-900 words per language. Structure
it as: (1) the question carta 01 left open and carta 02 answered; (2) the two
headline results — curvature pays at d=2 and stops paying on reconstruction by
d=5, and the pipeline's compression ratio turned out to reward degradation;
(3) the rename to semantic quantization and why the filenames still say
"compress"; (4) the figure; (5) what is NOT claimed; (6) where the evidence
lives (FINDINGS.md, phase2/README-fase2.md, one regenerate command).

DoD (binary), all five together:
  1. Both files exist and mirror each other's claims and numbers.
  2. The 1.55% token coverage appears BEFORE the first Phase-5 number in each
     note, and the reversal at d>=5 is stated without a budget reservation
     (dossier section 4b addendum authorises this).
  3. Zero sentences state a compression ratio as compression, compare against
     gzip or any entropy coder, or use the unit-free prototype ratio.
  4. Every number in the notes appears verbatim in FINDINGS.md, the Phase-4/5
     records of README-fase2.md, or a named out/ artifact — and the session
     report ends with a table mapping each number to its source.
  5. The three README links exist, and each targets the note in its own
     language (root README links both).

Rules:
  - No new measurement, no new number. This is a writing packet.
  - The figure is report/rate_distortion_wordnet-mammals_d2-5-10_
    seedset20260716x5.png, embedded by relative path from docs/
    (../phase2/report/... from docs/it/ and docs/en/ is wrong — count the
    levels: it is ../../phase2/report/...). Reuse the dossier's ready-made
    caption logic: iso-cost left panel, gold-hops right panel.
  - The matched-K result (Phase 5e) may be cited in one sentence at most — the
    pre-registered prediction, confirmed at d=10, with its one-clean-rung
    qualification. Do not build the note around it.
  - Ontrup & Ritter (2001) and Nickel & Kiela (2017, 2018) stay credited as the
    origin of the method; what is ours is the measurement.
  - Voice: honest and plain. The note reports a negative result as the main
    finding, because it is. No marketing, no "promising direction" filler.
  - Scope: ONLY the two new files and the three link lines. eval.py, harness/,
    embeddings/, ablation.py, compress.py, decode.py read-only; no other file
    under docs/ or the repo root; no .js; no figures regenerated.
  - F3 note: the one regenerate command quoted in each note is
      python compress.py --figure rate-distortion --out report/
    printed verbatim.

Environment: Windows host, interpreter from .venv-path, PYTHONSAFEPATH=1. stdout
is cp1252 — but this packet needs no Python at all unless verifying a number.

Finally: mark the Phase-6 row done with the date in README-fase2.md's phase
table, update the packet index (packets/README.md), and state in one sentence
what remains for Phase 7 (the sunset: tag v1.0 + NOT-DONE.md).
```

## Why this packet matters

Today a reader who finishes carta 02 and follows the repository link finds the
evidence only if they already know to open `phase2/FINDINGS.md`. The docs tree —
the part of the repository written for readers — still ends its story in 2025,
before anything was measured. This note is the difference between a repository
that contains its result and one that communicates it.
