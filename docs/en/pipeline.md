# The eight-step pipeline

← [Index](./README.md)

> 🎬 Want to see it in motion? Open the [animated pipeline](../diagram/pipeline.html). The same content told in prose below.

## Quick map

| # | Stage | What it does | Code |
|---|-------|--------------|------|
| 1 | Preprocess | Unicode normalize, tokenize | `compressionTest.js:90–95` |
| 2 | Co-occurrence | Count who appears near whom | `compressionTest.js:98–138` |
| 3 | Embedding | Reduce dimensions | `compressionTest.js:141–291` |
| 4 | Poincaré | Move points into curved space | `compressionTest.js:279–287` |
| 5 | Distance | Compute hyperbolic distance | `compressionTest.js:294–313` |
| 6 | Auto-threshold | Pick the cut for clusters | `compressionTest.js:453–573` |
| 7 | Clustering | Group via union-find | `compressionTest.js:575–659` |
| 8 | Estimate | Compute a *ratio* | `compressionTest.js:661–676` |

---

## 1 · Preprocess — clean and tokenize

The raw text is **NFKC-normalized** (to align diacritics, ligatures and typographic variants) and split into words. The regex is `/\p{L}{2,}/gu`: "Unicode letter sequences of length two or more". Punctuation, digits, symbols and single letters are dropped. The result is an ordered list of tokens. Without this step everything downstream is noise.

## 2 · Co-occurrence — who appears near whom

A **sliding window** of radius `windowSize` (default 3) walks across the tokens. For each centre word, the window's other words receive a count. The structure is a **sparse matrix**: each row is a `Map<column, count>`. Pairs that never met are simply absent — no memory wasted.

Two counting modes:

- **uniform**: each neighbour counts as 1.
- **distance**: closer neighbours count more (`1 / (1 + |i − j|)`).

Vocabulary is capped by frequency to `maxVocab` (default 5000). Rarer words are dropped because they would only contribute statistical noise.

## 3 · Embedding — squeeze the vocabulary into few dimensions

Each row is a long sparse vector. We need short vectors of dimension `dimension` (typically 2 or 3) so we can (a) compute distances in reasonable time, (b) optionally plot them.

Three strategies:

- **`random`** (default, robust): for each output axis, sum the count over a random subset of columns. Fast, deterministic given a `seed`, robust on sparse rows.
- **`firstD`**: take the first *D* columns of the matrix. Legacy, simple, useful for reproducing the historical behaviour.
- **`svd`**: dense SVD on the matrix (small vocabularies up to `svdMaxN`, default 800). Requires `ml-matrix` or `svd-js`; if missing, the pipeline gracefully falls back to `random`.

Vectors are then normalised (row / row-sum) and end up living roughly in `[0,1]^d`.

## 4 · Poincaré disk — into the curved space

The Euclidean vectors are **radially scaled** to live inside the unit disk:

```
x_poincaré = x · min(0.85 / ‖x‖, 1.0)
```

The 0.85 factor keeps points away from the boundary (where the geometry has singularities). All points satisfy `‖x‖ < 1`. From outside they look merely shifted; from inside, the disk's metric reshapes their notion of "closeness".

## 5 · Hyperbolic distance — Möbius at work

Distance between `u` and `v` uses the **Möbius metric**:

```
d_H(u,v) = acosh(1 + 2 · ‖u − v‖² / ((1 − ‖u‖²)(1 − ‖v‖²)))
```

Intuitively:

- Near the centre the distance behaves almost Euclidean.
- Near the boundary, a small Euclidean gap explodes into a huge hyperbolic gap. That is the "zoom" effect: the disk uncurls and the boundary becomes infinite.

Small *epsilon clamps* prevent numerical issues near the boundary.

## 6 · Auto-threshold — a self-calibrating ruler

Picking the clustering cut by hand is tedious. The prototype offers an automatic choice based on a **sample of pairwise distances** (up to `autoThresholdSample`, default 3000).

Three methods:

- **`percentile`**: pick the p-th percentile (default p35). Simple, robust on regular distributions.
- **`mad`**: robust cutoff via Median Absolute Deviation: `threshold = median − K · 1.4826 · MAD`. Resists outliers.
- **`hybrid`**: choose automatically. If the upper tail (p95 vs median, scaled by σ) is heavy, prefer MAD; otherwise percentile.

Enable `autoThresholdHistogramBins` to also receive a histogram of sampled distances. All these numbers (median, MAD, σ, percentiles, chosen method) flow back to the benchmark JSON when `--autoStats` is set.

On `samples/sample.txt` the system picks `percentile`, threshold ≈ 0.51, median ≈ 0.68, p95 ≈ 1.49.

## 7 · Clustering — union-find

We build a graph: words are nodes, two nodes are linked when their hyperbolic distance is below the threshold. Clusters are the **connected components** of this graph. Implementation: **union-find with path compression**. Order-independent, deterministic.

Cost: O(V²) pairwise checks. Mitigated by an optional **k-NN prefilter** (`clusterK > 0`): compute Euclidean k-NN first, evaluate the hyperbolic distance only for those pairs. Cost: ~O(V·K). Further: approximate k-NN with deterministic sampling (`approxKNN`, `approxKCandidates`).

For each cluster a **representative** is chosen: today, the first index encountered. The `center` is the vector mean of members.

On the Italian sample paragraph: **3 clusters** — one large (63 words: articles + prepositions + common verbs, represented by "la"), two singletons ("pensieri", "regolare").

## 8 · Compression estimate — a thermometer, not a codec

Toy model:

```
size_original = total token count
size_compressed ≈ #clusters + 0.5 · total tokens   (mapping overhead)
ratio = size_compressed / size_original
savings (%) = (1 − ratio) · 100
```

On `sample.txt`: ratio ≈ 0.455, savings ≈ 54.5%.

Take it for what it is: an **estimate of semantic density**. Fewer, well-populated clusters bring the ratio down. For a fair gzip-like comparison you would need a real entropy coder (see [improvements](./improvements.md)).

## Continue

➡️ [Hyperbolic geometry without heavy formulas](./soft-math.md)
