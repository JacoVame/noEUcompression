# Packet — Phase 6: article upgrade (carta 02, §4)

**What was located on 2026-08-04, so no session repeats the search.**

- **carta 01 is on disk**: `C:\Users\gianluca.g\Downloads\mappare_invisibile_v2.md`
  — *"Mappare l'Invisibile — SOM e Grandi Modelli Linguistici"*, Italian, ~17k
  characters, July 2026. Its structure is §1 Il Ponte Topologico, §2 Implicazioni
  architetturali, §3 Prospettive future, **§4 La questione della curvatura**,
  then *Sintesi* and *Cosa questo articolo non afferma*. A LinkedIn variant sits
  beside it (`mappare_invisibile_linkedin_v2_romantica.txt`).
- **carta 02 is "Misurare l'Invisibile"**: only its teaser image is on disk,
  `C:\Users\gianluca.g\Downloads\teaser_carta02_misurare_invisibile.png`
  (2026-08-03). The text lives in a Claude project (web side) per the PM, not on
  the filesystem, and not in the Obsidian vault. **The PM must paste or export
  it**; do not go hunting.
- **Why this phase exists, in the article's own words.** §4 of carta 01 says of
  this very repository: *«non apprende gli embedding (fa una proiezione casuale e
  un riscalamento radiale — usa la metrica curva, ma non colloca le parole per
  gerarchia)»*. Phases 2-4 closed exactly that gap: the embeddings are now
  learned by Riemannian optimisation on a gold hierarchy, and the comparison
  against a matched Euclidean baseline is measured, seeded and reproducible. The
  chart is that evidence.
- **The nuance that must survive editing.** §4 of carta 01 argues that hyperbolic
  space has room for trees because disc area grows exponentially with the radius.
  Phase 4 says this pays **where dimension is scarce** — decisively at d=2 — and
  stops paying on reconstruction by d=5, where the Euclidean baseline overtakes on
  MAP and mean rank. Carta 02 gains its credibility from reporting the second half.

Paste the block below as the opening message of a fresh session, after adding the
carta 02 text (or its path) at the marked point.

```text
Read ./CLAUDE.md and ./README-fase2.md. Current phase: 6 (article upgrade,
carta 02 "Misurare l'Invisibile" — §4 gains a real chart).

Precondition: Phase 4b (epoch-sensitivity addendum) must be done and recorded in
README-fase2.md, because the article may go to technical review and the epoch
budget is the one open methodological question. If 4b is not recorded, stop and
say so rather than writing around it.

Context you must read before writing, in this order:
  1. C:\Users\gianluca.g\Downloads\mappare_invisibile_v2.md — carta 01. Read §4
     ("La questione della curvatura") in full and the closing section "Cosa questo
     articolo *non* afferma". That §4 states that this repository does NOT learn
     its embeddings, only reuses the curved metric. Phase 2-4 is what changed
     that, and §4 of carta 02 is where the change gets reported.
  2. <<PM: paste the carta 02 text here, or give its path>>. Match its section
     numbering; if its §4 already exists, you are upgrading it, not appending.
  3. The Phase-4 result section of README-fase2.md.

This packet must NOT re-run experiments. Sources of truth, all read-only:
  - out/ablation_table_wordnet-mammals_dims2-5-10_seedset20260716x5.{json,md};
  - the three figures out/ablation_{map_vs_dimension,distortion_vs_depth,
    distance_spread}_wordnet-mammals_dims2-5-10_seedset20260716x5.png;
  - out/ablation_run_*.json for any per-seed number you cite.
If out/ is empty, regenerate it with the single Phase-4 command before writing —
artifacts are git-ignored by PM decision, so regenerating is the normal path and
takes ~3.5 h cold. Do not invent, round differently from, or re-derive numbers
the artifacts already state.

DoD (binary): §4 of carta 02 contains a real chart — at least the
MAP-vs-dimension figure, with mean ± σ over the 5-seed set visible and the seed
set named — plus prose in which every number traces to an artifact, and one
printed command that regenerates every figure and number cited.

Deliverable shape: if the PM gave a path, edit §4 of that file in place and
nothing else in it. Otherwise write a self-contained insert at
phase2/report/section4.md, in Italian, ready to paste, with the three figures
referenced by their out/ filenames and captions that stand alone.

Language and voice: Italian, matching carta 01 — first person, narrative but
technically exact, and comfortable saying what the work does not show. Do not
flatten it into a lab report, and do not inflate it into a press release.

Content requirements, in order of importance:
  1. The headline is the WHOLE result. Hyperbolic geometry wins unambiguously
     only at d=2 (MAP 0.7538 -> 0.8957, average distortion 0.3441 -> 0.2609);
     from d=5 the Euclidean baseline takes reconstruction outright, and at d=10 it
     reaches MAP 1.0000 / mean rank 1.0000 against 0.9853 / 2.4549. The
     distortion edge does not close monotonically (+0.0831 at d=2, -0.0012 at
     d=5, +0.0320 at d=10). Reporting only the d=2 win would be cherry-picking
     inside a phase set built to prevent exactly that — and it would contradict
     carta 01's own "cosa non afferma" discipline.
  2. Close the loop with carta 01 explicitly: §4 there confesses the embeddings
     were not learned; say that they now are, by Riemannian optimisation on the
     Lorentz model against a WordNet gold hierarchy, and that the comparison is
     matched per geometry.
  3. State the fairness protocol, because it is the article's defence: per-
     (geometry, dimension) learning rates tuned on synthetic-tree only and frozen
     before any wordnet run; the report set run once; the epoch budget held at
     6000 for both geometries with 4b's sensitivity result attached.
  4. Report the mean-rank penalty as a mechanism, not a footnote: hyperbolic mean
     rank is worse at every d, and the spread figure shows why — hyperbolic is
     *under*-spread against the graph metric (σ/mean 0.135 vs 0.293) while
     Euclidean at d=2 is over-spread (0.513). This is the measured form of the
     crowding that §1 and §4 of carta 01 discuss qualitatively.
  5. Say that MAX_SPATIAL_NORM 1e4 is a numerical guard and quantify its reach
     (721/1170 nodes at d=2, ~7% at d=5 and d=10), so no reviewer can mistake it
     for a capacity knob that manufactured the result.
  6. Keep the non-goals visible: no gzip comparison, no claim of real
     compression, no Poincaré-GloVe, and the honest citation of prior art that
     carta 01 already makes (Ontrup & Ritter's hyperbolic SOM, NIPS 2001; Nickel
     & Kiela 2017/2018). This is a geometry measurement on a gold hierarchy.

Scope: create only the section text (or edit §4 of the document the PM supplied).
Do not touch eval.py, harness/, embeddings/, or the sealed parts of ablation.py;
do not edit the JS companion; do not restyle the figures to suit the article — if
a figure is unusable as published, say why instead of quietly replacing it.
```
