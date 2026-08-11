# Packet — Phase 5e (addendum): the matched-K comparison Phase 5b owed

**Why this packet exists.** Phase 5b's DoD rested on a rule it called load-bearing —
*matched K, not matched percentile* — and on a matched-K re-run of the d=2
comparison as a deliverable rather than an extra. Neither was delivered: the
`--dims` implementation reuses Phase 5's percentile grid, so K differs between
sides at every operating point. The pre-registered prediction (`README-fase2.md`,
Phase-5 section) is explicitly a statement about **K-matched** operating points at
d=10, with a falsification condition stated at matched K, so the prediction was
never actually tested. The Phase-5b record says all of this itself; this packet
closes it.

Authorised by the PM on 2026-08-11, in the same session as the dossier refresh —
a deliberate exception to the one-session-one-phase rule, recorded here rather
than left implicit.

```text
Read ./CLAUDE.md and ./README-fase2.md. Current phase: 5e (addendum to Phase 5b).

Deliver the matched-K comparison and nothing else. Do not restate the Phase-5b
conclusion, do not adjust anything to make a ranking come out a particular way,
and do not soften the outcome if it contradicts the pre-registered prediction.

Scope. compress.py: ADDITIVE change only, a --matched-k option beside the existing
--dims. Untouchable: the lemma->synset mapping path, the percentile-threshold grid,
the accounting (bits_per_token_after, residual_bits_per_token, ratio, ratio_ideal),
the gold_hops computation, and every existing artifact in out/. eval.py, harness/,
embeddings/, ablation.py and decode.py stay read-only. The JS companion stays out
of scope.

DoD (binary): ONE command produces, for every dimension and every rung of a K
ladder, the three-side comparison of gold_hops_token_weighted at MATCHED cluster
count, with the achieved K printed beside every figure, mean +/- sigma over the
five seeds; plus, per dimension and per rung, whether the euclidean-vs-lorentz
gold-hops order matches the Phase-4 MAP ranking, the distortion ranking, the
embedded-spread ranking, all of them or none. Target command:

  python compress.py --matched-k 80 60 40 20 --dataset wordnet-mammals --dims 2 5 10 --seeds 5 --out out/

Rules:
  - K is matched PER SIDE PER SEED: for each target K, search that cell's own
    threshold ladder for the achieved K closest to the target. Report the achieved
    K, never the target, next to every number.
  - Tolerance, stated because a rung that misses is not a rung: accept a cell if
    |achieved - target| <= max(2, 5% of target). If any side of a (dimension, rung)
    cell misses, DROP the whole rung for that dimension and name it in the report
    with the K each side could actually reach. A rung compared across sides at
    different K is the confound this packet exists to remove.
  - The prototype's auto-threshold clamp ([1e-6, 10]) is NOT applied on this path:
    matching K requires thresholds the percentile path cannot express. That is the
    point, and it is also a cost — report, per cell, whether the matched threshold
    falls outside the prototype's clamp window, because such a cell is unreachable
    by the prototype's own auto-threshold and therefore says something about the
    geometry rather than about the prototype.
  - Reuse the Phase-3/Phase-4 embedding checkpoints in out/ and the cached
    coordinate sets. Do not retrain. Missing cell -> report which and stop.
  - The js-cooccurrence side is carried forward from d=2 as in Phase 5b, but its
    coordinates must be re-derived to search its own thresholds; it is constant by
    construction across dimensions and must be said to be.
  - The mapping invariant (259 mapped types / 166 nodes) must hold, checked and
    not assumed.
  - Same seed set {20260716..20260720}, mean +/- sigma on every reported quantity.
  - F3: --seed default 20260716, artifacts into out/ with the seed set in the
    filename, every stated number regenerable by the one printed command.

Report as findings, not footnotes:
  - Whether the pre-registered prediction is confirmed or falsified at d=10 under
    matched K. The prediction: at K-matched operating points at d=10, the Euclidean
    side produces fewer token-weighted gold hops than the Lorentz side. State the
    verdict in one sentence, with the numbers, and quote the prediction only after
    the numbers exist.
  - Whether the published d=2 conclusion changes once K is matched. The published
    percentile-matched d=2 figures are lorentz 3.16 hops at K=72 against euclidean
    1.74 at K=85.
  - Whether Phase 5b's d>=5 euclidean result survives. Under the percentile grid
    euclidean was clamp-bound at d=5/d=10 with K = 165.6/166.0 of 166 nodes -- it
    clustered nothing, so its near-zero gold hops was not evidence about geometry.
    Matched K forces a real clustering; say what it shows.
  - Which of the three Phase-4 rankings the matched-K order tracks, per dimension
    and per rung, including "none".
  - The design limit that remains: MAP ranking and spread ranking are identical
    across d={2,5,10}, so this cannot separate those two; it separates both jointly
    from the distortion ranking, which differs at d=10 alone.

Environment: Windows host, interpreter from .venv-path, PYTHONSAFEPATH=1. stdout is
cp1252 -- printing a sigma raises UnicodeEncodeError; Unicode belongs in UTF-8
files and matplotlib titles only.

Runtime: minutes. The coordinates are cached; this is threshold search, clustering
and accounting.

Finally: add a Phase-5e row to the phase table in README-fase2.md marked done with
the date, record the result under the Phase-5 section, and correct the Phase-5b
record's open item so it points at this phase instead of at a gap.
```

## Why this packet matters

It converts the one unmet DoD clause in the programme into a measurement, and it
is the only thing that can make the pre-registered prediction testable. Either
outcome is publishable: a confirmation makes the embedded-spread/MAP story
downstream-relevant, a falsification hands distortion the practical meaning
instead. What is not acceptable is closing the project with the prediction
untested and the gap merely documented.
