# FINDINGS — what the phase-2 experiment actually measured

> One result, written down with its numbers, its artefact filenames and the two
> framing constraints that keep it honest. Everything here is already in `out/`;
> nothing was re-measured to write this document.
> Date: 2026-08-11 · dataset `wordnet-mammals` · seeds 20260716..20260720
> (`seedset20260716x5`) · mean ± σ over the seed set, never a single seed.
>
> **Coverage, before anything else: every number in this document describes 4616
> of the corpus's 297_697 tokens — 1.55%.**

## The one-sentence result

**The compression ratio this pipeline reports is a metric that rewards
degradation**: across the measured grid, the better the ratio, the further the
merges travel in the gold hierarchy — and the best ratio of the three sides
belongs to the most degenerate embedding in the study.

Nobody was gaming the metric. It happened because the metric was gameable.

## What this pipeline is (the reframe)

It is not compression. It is **semantic quantization**: types are quantized onto
cluster ids, and the honest evaluation plane is **rate–distortion** — bits per
token against semantic damage, both measured, neither traded silently.

The word "compress" survives in filenames (`compress.py`, `out/compress_*`) and
in every printed regenerate command. Those names are load-bearing for F3
reproducibility: renaming them would invalidate the commands that regenerate
every number in this repository. They are historical labels, not claims.

## Coverage first, before any ratio appears

Every number below describes **1.55% of the corpus**.

| quantity | value | artefact |
|---|---|---|
| tokens encoded (N) | 4616 of 297_697 (**1.55%**) | `out/compress_mapping_pg2300_wordnet-mammals.json` |
| tokens dropped as unmapped | 293_081 (98.45%) | same |
| types mapped (V) | 259 of 13_565 | same |
| synsets reached = nodes clustered | 166 of 1170 (14.2%) | same |
| type entropy of the mapped stream | 5.696 bits/token | same |

The corpus is Darwin, *The Descent of Man* (Project Gutenberg #2300, sha256
`2911dfcc2b0b498f…`, pinned and verified on every run). A ratio computed on 1.55%
of a text is a statement about that 1.55%, and about nothing else.

## (a) The ratio anti-correlates with fidelity

Pearson *r* over every (side, percentile) cell of the grid — 3 sides × 12
percentiles = **36 cells per dimension**, each cell a mean over 5 seeds.

| d | r(ratio, gold hops) | r(ratio, largest-cluster token share) | cells | artefact |
|---|---|---|---|---|
| 2 | **−0.841** | **−0.949** | 36 | `out/compress_wordnet-mammals_d2_seedset20260716x5.json` |
| 5 | **−0.992** | **−0.712** | 36 | `out/compress_dims_wordnet-mammals_dims5-10_seedset20260716x5.json` |
| 10 | **−0.984** | **−0.654** | 36 | same |

`ratio` falls as the code gets shorter, so a *negative* r against gold hops means:
**the cells with the best ratios are the cells whose merges span the most hops in
the frozen hierarchy.** The same sign holds against the largest cluster's token
share — the best ratios are the ones that dump the most of the corpus into one
bucket.

**Higher dimensions do not weaken the finding; they split it.** The gold-hops
anti-correlation *strengthens* at d=5 (−0.992) and d=10 (−0.984); the
largest-cluster-share anti-correlation *weakens* at both (−0.712, −0.654). The
headline result is the gold-hops one, and it is the one that survives the
dimension sweep. Reported as measured, in both directions.

**A definitional caveat, because it changes the digits and not the conclusion.**
The Phase-5 record and the Phase-5b summary quote the d=2 reference as
**−0.88 / −0.92**. That pair is computed on `ratio (no ceil)`, the fractional-bit
ratio; the d=5 and d=10 numbers in the same summary are computed on the integer
fixed-width `ratio`. Recomputed like-for-like on the integer ratio, d=2 reads
**−0.841 / −0.949** (the fractional-ratio pair is −0.879 / −0.921, which is the
published one). The table above is the like-for-like comparison. Both definitions
give the same sign, the same order of magnitude and the same conclusion; only the
two decimals move. Regenerate either with
`compress.ratio_fidelity_correlation(<aggregate>)` on the JSON named in the
table.

### The three cells that make the abstraction concrete

At d=2 (`out/compress_wordnet-mammals_d2_seedset20260716x5.json`,
`out/compress_run_<side>_wordnet-mammals_d2_seed<seed>.json`):

| cell | K | ratio | gold hops | largest cluster | what it is |
|---|---|---|---|---|---|
| lorentz, p=0.35 | 6.40 ± 2.65 | **0.3286 ± 0.1150** | 7.49 ± 0.12 | **0.8734** | best ratio on the learned side |
| js-cooccurrence, p=0.01 | 19.20 ± 8.26 | **0.5633 ± 0.1150** | 7.65 ± 0.02 | 0.5129 | best ratio of the three sides |
| euclidean, p=0.01 | 85.20 ± 1.72 | 0.8214 ± 0.0000 | **1.74 ± 0.06** | 0.3388 | most faithful merges, worst ratio |

- **The best ratio of the three sides belongs to the unlearned heuristic.** The
  js-cooccurrence baseline's pairwise distances are **84.9% ± 7.9% exactly zero**
  at d=2 — its 16-random-feature projection sends every low-mass row to the
  origin — so its clustering is "merge coincident points", and its merges span
  7.65 ± 0.02 hops against the hierarchy-blind 7.654. It is the most degenerate
  embedding in the study and it wins the metric.
- **The Lorentz side's own best ratio puts 87.3% of the tokens in one cluster**,
  with merges spanning 7.49 hops — i.e. statistically indistinguishable from a
  clustering that ignores the hierarchy altogether.
- **The hierarchy-blind reference is 7.654 hops**: the all-pairs mean shortest
  path over the same 166 synsets in the frozen hierarchy. Re-derived, not
  transcribed, by `python compress.py --figure rate-distortion --out report/`,
  which prints it.

**A corollary, measured in Phase 5e.** Hold the cluster count fixed instead of the
percentile and the ratio becomes *identical* on both learned sides by construction —
same K, same N, same V, so the same code length — while the gold hops still differ
by up to 1.65 (d=10, K=40: 4.856 ± 1.189 against 6.506 ± 0.152). At fixed K the
ratio carries **no** information about semantic damage: not a weak signal, none.
The anti-correlation above is what that looks like when K is allowed to vary, which
is the only way the ratio moves at all
(`out/compress_matchedk_wordnet-mammals_dims2-5-10_k80-60-40-20_seedset20260716x5.json`).

## (b) The iso-cost diagonal — stated as internal accounting

Under the code this repository declares (fixed width, no entropy coder,
`out/compress_wordnet-mammals_d2_seedset20260716x5.json` field `code`), each cell
has a code length `⌈log2 K⌉` bits/token and a measured residual
`H(type | cluster)` bits/token that a decoder would still need. Their **sum**:

| d | cells | code + residual, min … max | before any clustering |
|---|---|---|---|
| 2 | 36 | 7.967 … 8.885 bits/token | 9.00 bits/token, zero loss |
| 5 | 36 | 8.136 … 9.950 bits/token | 9.00 bits/token, zero loss |
| 10 | 36 | 8.135 … 10.004 bits/token | 9.00 bits/token, zero loss |

Every configuration falls on essentially the same diagonal: **bits are moved out
of the code and into the loss, roughly one for one, rather than saved.** The
ratio only ever reports the first coordinate.

This needs no rival codec to be true. It is arithmetic internal to the accounting
this repository already publishes — which is why it is the form the result is
stated in.

**And in 18 cells the move is a net loss.** At d=5 and d=10 the nine
lorentz cells at p ≥ 0.02 price at 9.95 / 10.00 bits/token — *more* than the 9.00
bits/token the same code spends with no clustering at all
(`out/compress_wordnet-mammals_d{5,10}_seedset20260716x5.json`). A shorter code,
a longer total.

## (c) The reference floor — and the comparison that is deliberately not made

The stated code spends **9 bits/token** (`⌈log2 259⌉`) before clustering. The same
mapped type distribution has entropy **5.696 bits/token**
(`out/compress_mapping_pg2300_wordnet-mammals.json`, `type_entropy_bits`). The
difference, **3.304 bits/token, is the declared baseline's own slack**, identical
on every side because `N` and `V` are identical on every side by construction.

**Consequence for reading any ratio in this repository: a ratio measured against
`size_before` is partly measuring that slack, not the geometry.**

`CONSTRAINTS.md` names "no comparison against `gzip` or any entropy coder" as a
binding non-goal of this work, and that non-goal binds this document too. The
5.696 bits/token figure appears here as a **reference floor that measures how
loose the stated fixed-width code is** — not as a competitor, and not as evidence
about what any other method would achieve.

The distinction is not pedantry, and it is worth stating in the two sentence
forms:

- *"the pipeline is worse than X"* — **out of scope.** It violates a declared
  non-goal, and it needs a rival that was never run.
- *"the declared baseline has 3.3 bits/token of slack, so the ratio partly
  measures the baseline"* — **in scope.** It is the actual result, it needs no
  rival, and it is checkable from the artefacts named above.

An earlier reading of this same arithmetic stated it in the first form. The
arithmetic was right and the framing was not; the iso-cost diagonal in (b) says
the same thing without a rival, and is unattackable because it is internal.

## (d) The cost accounting is verified by an actual round trip

`out/decode_verify_wordnet-mammals_d2_seedset20260716x5.{json,md}`.

At **every one of the 180 grid cells** (3 sides × 12 percentiles × 5 seeds, d=2)
the cost reconstructed from a real encode→decode round trip equals the stored
`bits_per_token_after + residual_bits_per_token` to within **1.066e-14
bits/token**, against a stated gate tolerance of **1e-9**. The command exits
non-zero on any failure; it exits 0.

**The exact-match rate is that loss made concrete** — the share of tokens a
decoder reproduces verbatim:

| cell | exact match | with a random cluster representative |
|---|---|---|
| euclidean, p=0.01 | 0.6811 ± 0.0124 | 0.3051 |
| lorentz, p=0.01 | 0.6250 ± 0.0264 | 0.2182 |
| js-cooccurrence, p=0.01 | 0.5138 ± 0.0626 | 0.4820 |
| euclidean, p=0.35 | 0.5017 ± 0.0716 | 0.1312 |
| **lorentz, p=0.35** (the best ratio) | **0.2867 ± 0.0179** | 0.0076 |

Every ratio this repository prints buys its bits at these odds. The canonical
representative rule (highest-frequency type in the cluster) is worth roughly a
factor of 2 where a real clustering exists and a factor of 38 inside a giant
cluster, so the second column is the bound on how much of the first is the
decoder's tie-breaking rule rather than the geometry.

## What a good ratio costs, concretely

One cell, from the artefacts rather than invented — the Lorentz side at p=0.35,
seed 20260716
(`out/decode_verify_wordnet-mammals_d2_seedset20260716x5.json`, `per_seed`):

- **6 distinct codes** emitted for 259 types, a **3-bit** code,
- ratio **0.3286** — the best number anywhere on the learned sides,
- **73.2% of decoded tokens are the wrong word** (exact match 0.2680),
- residual, measured on the round trip's own (code, type) pairs: **5.656
  bits/token** — so the three bits saved cost 5.7, and the total lands back on the
  diagonal at 8.656.

The Phase-5 record documents what those merges look like when a real clustering
survives: at p=0.01, seed 20260716, the Euclidean side's second-largest cluster is
the ape clade (`anthropoid, ape, chimpanzee, gibbon, gorilla, orang, siamang,
simian`) while the Lorentz side merges the canines *with the elephants*
(`dog, dogs, jackal, cur, canine, elephant, elephants`, 24 types) — and the
Lorentz side is the one with the better fractional ratio at that operating point
(0.8133 vs 0.8448). Winning the ratio and clustering faithfully are opposite
things here (`README-fase2.md`, Phase-5 record, 2026-08-04).

## The figure

Two panels, both drawn from the aggregates already in `out/` — code length
against residual loss with the iso-cost diagonals and the two zero-loss reference
points, and code length against gold hops with the hierarchy-blind reference
line:

```
python compress.py --figure rate-distortion --out report/
```

Writes `report/rate_distortion_wordnet-mammals_d2-5-10_seedset20260716x5.png`
(108 cells: 3 sides × 12 percentiles × 3 dimensions). It measures nothing, writes
nothing into `out/`, and prints the hierarchy-blind reference it re-derives from
the frozen hierarchy (7.6540 over the 166 clustered synsets).

## Scope of the claim

- One corpus, one hierarchy, **1.55% token coverage**, d ∈ {2, 5, 10}, 5 seeds.
- The prototype's auto-threshold clamp ([`compressionTest.js:531-535`](https://github.com/JacoVame/noEUcompression/blob/v1.0/compressionTest.js#L531-L535),
  bounds `[1e-6, 10]`) binds on several cells; where it binds, the clamp and not the
  percentile decides the clustering, and at d=5/d=10 the Euclidean side merges
  almost nothing (K = 165.6 / 166.0 of 166 nodes, ratio 0.9388 = the
  no-clustering floor). Those cells say nothing about geometry, and are marked as
  such in the Phase-5b record. **Phase 5e (2026-08-11) re-read the same
  embeddings at matched cluster count**, off the clamped percentile path, and the
  clamp-bound cells become real clusterings: Euclidean produces 1.85–7.06
  token-weighted gold hops at K = 80…20 instead of ~0. That measurement does not
  touch anything above — every ratio, correlation and round-trip figure in this
  document is percentile-indexed and unchanged — but it is where to look before
  reading the d≥5 Euclidean cells as evidence about geometry
  (`out/compress_matchedk_wordnet-mammals_dims2-5-10_k80-60-40-20_seedset20260716x5.json`).
- The finding is about **this metric on this pipeline**. It generalises as a
  caution — *a quality metric that improves monotonically as information is
  discarded will be optimised by discarding information* — not as a measurement
  of anything outside this grid.

---

<sup>**Footnote on a number not used here.** The aggregates carry a third,
unit-free ratio inherited from the prototype's own documentation, which divides a
vocabulary-sized quantity by a token count. Read naively it looks like a
compression figure above 90%, and it is not comparable to anything else in this
document: numerator and denominator count different things. It appears nowhere in
this document, and no number here is derived from it.</sup>
