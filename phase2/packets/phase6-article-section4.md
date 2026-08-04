# Packet — Phase 6: article upgrade (carta 02, §4)

**Where carta 02 is: unknown, and searched for.** On 2026-08-04 a search found no
candidate anywhere reachable from the build host — not in this repository (the
string `carta` appears only in `README-fase2.md`), not in the sibling folders
under `R:\CodeSpace\Bride` (`docs/`, `artifacts/`, `briglia/` belong to a
different project), and not in the Obsidian vault (no hit for `noEUcompression`
nor for `carta`). The document lives wherever the article series is kept, off this
machine. The brief therefore defaults to producing a self-contained insert; do not
spend the session hunting for the file again. If the PM supplies a path, replace
the "WHERE THE TEXT GOES" paragraph with it before pasting.

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md and ./README-fase2.md. Current phase: 6 (article upgrade,
carta 02 — §4 gains a real chart).

Precondition: Phase 4b (epoch-sensitivity addendum) must be done and recorded in
README-fase2.md, because the article is going to technical review and the epoch
budget is the one open methodological question. If 4b is not recorded, stop and
say so rather than writing around it.

The material already exists and this packet must NOT re-run experiments. Sources
of truth, all read-only:
  - the Phase-4 result section in README-fase2.md (table, conclusion, findings);
  - out/ablation_table_wordnet-mammals_dims2-5-10_seedset20260716x5.{json,md};
  - the three figures out/ablation_{map_vs_dimension,distortion_vs_depth,
    distance_spread}_wordnet-mammals_dims2-5-10_seedset20260716x5.png;
  - out/ablation_run_*.json for any per-seed number you cite.
If out/ is empty, regenerate it with the single Phase-4 command before writing —
artifacts are git-ignored by PM decision, so regenerating is the normal path and
takes ~3.5 h cold. Do not invent, round differently from, or re-derive numbers
that the artifacts already state.

WHERE THE TEXT GOES. "carta 02" is not reachable from this machine: a search on
2026-08-04 found no candidate in the repository, in the sibling project folders,
or in the Obsidian vault. So unless the PM gives you the path, the deliverable is
a self-contained insert at phase2/report/section4.md, written to be pasted into
§4 as-is, with the three figures referenced by their out/ filenames and captions
that stand alone. Do not go looking for the file. If the PM does give a path,
edit that file in place and nothing else in it beyond §4.

DoD (binary): §4 contains a real chart — at least the MAP-vs-dimension figure,
with mean ± σ over the 5-seed set visible and the seed set named — plus prose in
which every number traces to an artifact, and one printed command that
regenerates every figure and number cited.

Content requirements, in order of importance:
  1. The headline must be the WHOLE result, not the flattering half. Hyperbolic
     wins unambiguously only at d=2 (MAP 0.7538 -> 0.8957, distortion 0.3441 ->
     0.2609); from d=5 the Euclidean baseline takes reconstruction outright, and
     at d=10 it reaches MAP 1.0000 / mean rank 1.0000 against 0.9853 / 2.4549.
     The distortion edge does not close monotonically (+0.0831 at d=2, -0.0012 at
     d=5, +0.0320 at d=10). An article that reports only the d=2 win would be
     cherry-picking within a phase set built to prevent exactly that.
  2. State the fairness protocol, because it is the article's defence: per-
     (geometry, dimension) learning rates, tuned on synthetic-tree only, frozen
     before any wordnet run; the report set run once; the epoch budget held at
     6000 for both geometries with 4b's sensitivity result attached.
  3. Report the mean-rank penalty as a mechanism, not a footnote: hyperbolic mean
     rank is worse at every d, and the spread figure shows why — it is
     under-spread against the graph metric (σ/mean 0.135 vs 0.293) while
     Euclidean at d=2 is over-spread (0.513).
  4. Say that MAX_SPATIAL_NORM 1e4 is a numerical guard and quantify its reach
     (721/1170 nodes at d=2, ~7% at d=5 and d=10), so no reviewer can mistake it
     for a capacity knob that manufactured the result.
  5. Keep the README non-goals visible: no gzip comparison, no claim of real
     compression, no Poincaré-GloVe. This is a geometry measurement on a gold
     hierarchy, and saying so is what makes the d=2 claim survive review.

Scope: create only the section text (and, if the PM supplies the path, edit §4 of
that document). Do not touch eval.py, harness/, embeddings/, or the partially
sealed parts of ablation.py; do not edit the JS companion; do not regenerate the
figures with different styling to suit the article — if a figure is unusable as
published, say why instead of quietly replacing it.

Language: agent-facing docs in phase2/ are English. Match the language of carta
02 itself for the section text, and state which you used.
```
