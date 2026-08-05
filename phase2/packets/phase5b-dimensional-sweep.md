# Packet — Phase 5b (addendum): the dimensional sweep in the pipeline

**PM precondition — do not skip, do not delegate.** Before pasting the block below, the PM commits a one-paragraph prediction to `README-fase2.md` under the Phase-5 section, stating which Phase-4 geometric metric is expected to predict downstream semantic fidelity, and why. That commit must precede the session commit. The prediction is deliberately **not** reproduced in the brief: an agent that knows the expected outcome can steer toward it, and Phase 5 already measured what happens when a metric is visible to the thing being optimised. The validator check is mechanical — `git log` must show the prediction commit before the results commit.

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md and ./README-fase2.md. Current phase: 5b (addendum to Phase 5).

Phase 5 ran the quantization pipeline at d=2 only. At d=2 the two Phase-4
geometric metrics agree — the Lorentz side wins both MAP and average distortion —
so d=2 cannot tell which of them predicts downstream behaviour. At d=5 and d=10
they disagree: the Euclidean side reconstructs better (perfect MAP at d=10) while
distorting the global metric more. That disagreement is the experiment.

Deliver the measurement and nothing else. Do not interpret the result against any
expected outcome, do not adjust anything to make a ranking come out a particular
way, and do not read the Phase-5 prediction paragraph in README-fase2.md until
after your numbers are written to out/ and committed.

Scope. compress.py: ADDITIVE change only. Untouchable: the lemma->synset mapping
path, the percentile-threshold grid, the accounting (bits_per_token_after,
residual_bits_per_token, ratio, ratio_ideal), and the gold_hops computation. The
additive case is a --dims option that runs the existing pipeline against
embeddings at other dimensions. eval.py, harness/, embeddings/euclidean.py and
embeddings/lorentz.py stay read-only. ablation.py stays untouched entirely. The JS
companion in the repo root stays out of scope.

The admissibility test is mechanical and you must run it: the regression gate must
still pass, to the digit, on all four cells, and the d=2 Phase-5 aggregate must
reproduce byte-identically from the existing checkpoints.

DoD (binary): ONE command produces the three-side pipeline aggregate at d=5 and
d=10, and a table stating, per dimension, the ranking of the sides by
gold_hops_token_weighted next to their Phase-4 MAP ranking and their Phase-4
distortion ranking. Target command:

  python compress.py --dataset wordnet-mammals --dims 5 10 --seeds 5 --out out/

Rules:
  - MATCHED K, NOT MATCHED PERCENTILE. This is the load-bearing rule of the
    packet. The existing grid is indexed by percentile threshold, and equal
    percentiles give DIFFERENT cluster counts across sides (at d=2, p=0.01 gives
    K=85.2 euclidean and K=72.2 lorentz). Gold hops rises mechanically as K falls,
    because fewer clusters means coarser merges, so any comparison at unmatched K
    is confounded and cannot answer this packet's question. Compare sides at
    common K values: pick a K ladder that both sides can reach (e.g. K in
    {80, 60, 40, 20}), and for each side and each target K select the threshold
    whose mean K is closest, reporting the achieved K alongside every number. If a
    side cannot reach a target K within a stated tolerance, drop that rung and say
    which.
  - Report the d=2 cells under the same matched-K treatment as well. The published
    Phase-5 d=2 comparison is percentile-matched and therefore confounded; the
    matched-K version of it is a deliverable of this packet, not an extra.
  - The lemma->synset mapping is dimension-independent: the same 259 mapped types
    and 166 reached synsets must appear at every d. If they do not, the mapping is
    being rebuilt and that is a defect — stop and report it.
  - Reuse the Phase-3/Phase-4 embedding checkpoints in out/. Do not retrain. If a
    checkpoint for a (geometry, d, seed) cell is missing, report which and stop;
    do not silently substitute a fresh training run.
  - The js-cooccurrence side is dimension-independent by construction (unlearned
    heuristic over 259 types). Carry it forward unchanged as a constant reference
    row, and say in the report that it is constant by construction rather than
    measured per dimension.
  - Same percentile grid as Phase 5, same seed set {20260716..20260720}, mean and
    sigma across seeds on every reported quantity.
  - F3: --seed default 20260716, every artifact into out/ with the seed set
    identified exactly in the filename, any stated number regenerable by one
    printed command.

Report as findings, not footnotes:
  - Per dimension, at each rung of the matched-K ladder, the three-side ranking by
    gold_hops_token_weighted, with sigma and with the achieved K printed next to
    each figure.
  - Whether that ranking matches the Phase-4 MAP ranking, the Phase-4 distortion
    ranking, the Phase-4 embedded-spread ranking (distance of
    emb_spread_sigma_over_mean from the graph's 0.2927), all of them, or none, at
    each dimension. "None" is a legitimate and interesting outcome: report it
    plainly instead of forcing a match.
  - NOTE for interpretation, stated here so it is not discovered late: across
    d={2,5,10} the MAP ranking and the spread ranking are IDENTICAL (lorentz,
    euclidean, euclidean), so this design cannot separate those two hypotheses. It
    can only separate them jointly from the distortion ranking (lorentz,
    euclidean, lorentz), which differs at d=10 alone. Say so in the report rather
    than claiming a resolution the design cannot deliver.
  - Whether the d=2 conclusion changes once K is matched. It may: the published
    d=2 numbers have lorentz at 3.16 hops against euclidean at 1.74, at K=72 and
    K=85 respectively.
  - Whether the ratio-vs-fidelity anti-correlation measured at d=2 (-0.88 against
    gold hops, -0.92 against largest-cluster token share, over 36 cells) holds,
    weakens or reverses at d=5 and d=10. This is the second question this packet
    can answer for free.
  - The correlation numbers with their cell counts, so they are checkable.

Environment: Windows host, interpreter recorded in .venv-path, always invoked by
that path, PYTHONSAFEPATH=1. WARNING: stdout is cp1252 — printing 'σ' raises
UnicodeEncodeError; funnel printed text through the existing console helper.
Unicode belongs in UTF-8 files and matplotlib titles only.

Runtime: the embeddings exist, so this is clustering plus accounting only —
minutes, not hours. If anything takes longer than that, something is being
recomputed that should have been loaded.

Finally: add a Phase-5b row to the phase table in README-fase2.md marked done with
the date, record the result under the Phase-5 section, and state in one sentence
whether the outcome is consistent with the PM prediction committed beforehand —
quoting the prediction only after your numbers are committed.
```

## Why this packet matters

It is the only experiment Phase 5 made possible without running. If downstream semantic fidelity at d=10 tracks **distortion** rather than **MAP**, then distortion is the geometric metric that matters for real tasks, and carta 02 acquires a practical meaning retroactively. If it tracks MAP, §4 of carta 02 needs correcting. Either way the answer is binary and cheap, and it is the difference between a measurement that delimits and one that builds.
