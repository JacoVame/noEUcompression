# HyperbolicTextCompressor

A small, self-contained prototype that explores semantic "compression" of text by mapping words into the Poincaré disk (hyperbolic space), clustering them by hyperbolic distance, and estimating a toy compression ratio.

This is research/prototyping code: it’s not a general-purpose compressor. It’s meant to help you experiment with non‑Euclidean geometries for text representation and get intuition about cluster-based compression ideas.

## Highlights

- Unicode‑aware preprocessing (keeps diacritics, drops 1‑letter tokens)
- Sparse co‑occurrence matrix with configurable window and distance weighting
- Fast, robust heuristic embeddings into the Poincaré disk
- Order‑invariant union‑find clustering by hyperbolic distance
- Deterministic runs with seed and tunable verbosity
- Embedded smoke tests you can run locally
- Optional auto‑tuned clustering threshold from a percentile of distances
- Quick benchmark harness to compare settings across inputs
- Optional auto-threshold diagnostics: median, MAD, sigma, p95, and chosen method

## Quick start

Prerequisites: Node.js 16+.

```powershell
# Windows PowerShell
node .\compressionTest.js
```

You’ll see a demo report on a built-in Italian sample paragraph, including cluster summaries and an estimated compression ratio.

## Usage in code

```js
const HyperbolicTextCompressor = require('./compressionTest');

const c = new HyperbolicTextCompressor(2, {
  maxVocab: 3000,
  seed: 42,
  windowSize: 3,
  clusterThreshold: 0.4,
  projection: 'random',            // 'random' | 'firstD' | 'svd'
  randomFeaturesPerDim: 16,        // only for 'random' projection
  weighting: 'distance',           // 'uniform' | 'distance'
  normalize: true,                 // Unicode NFKC normalization
  verbose: true,
  svdMaxN: 800,                    // max size for SVD projection
  clusterK: 0,                     // k-NN prefilter for clustering (0 disables)
  approxKNN: false,                // when clusterK>0, sample candidate neighbors instead of scanning all
  approxKCandidates: 50,           // number of candidates per node for approximate k-NN
  autoThreshold: false,            // enable auto-tuned threshold from pairwise distances
  autoThresholdPercentile: 0.35,   // percentile in [0,1] used if autoThreshold=true
  autoThresholdSample: 3000,       // max sampled pairs to estimate the percentile
  autoThresholdMethod: 'percentile', // 'percentile' | 'mad' | 'hybrid'
  autoThresholdMADK: 0.5,          // for 'mad': threshold = median - K * 1.4826 * MAD
  autoThresholdHistogramBins: 0,   // build histogram of sampled distances (0 disables)
  diagnosticsOnly: false           // skip clustering; return only auto-threshold diagnostics
});

const res = c.analyzeAndCompress('your text here');
console.log(res.compressionRatio);
```

### Constructor options

- dimension: integer >= 2, default 2
- maxVocab: cap the vocabulary (default 5000)
- windowSize: co‑occurrence window radius (default 3)
- clusterThreshold: hyperbolic distance threshold for clustering (default 0.4)
- projection: embedding projection strategy
  - random: more robust; each embedding dimension aggregates a random subset of co‑occurrence columns (default)
  - firstD: keeps the historical behavior (uses first D columns of each row)
  - svd: uses SVD on the dense matrix (n x n) for small n, then projects into the Poincaré disk; falls back if SVD deps missing
- randomFeaturesPerDim: how many co‑occurrence columns to sample per embedding dimension (default 16)
- weighting: co‑occurrence weighting
  - uniform: each neighbor counts 1
  - distance: neighbors are weighted by 1/(1+|i−j|) inside the window
- normalize: apply Unicode NFKC before tokenization (default true)
- verbose: print timings and steps (default true)
- seed: integer for PRNG determinism (affects random projection and fallback vectors)
- svdMaxN: SVD is attempted only when vocab size n <= svdMaxN (default 800)
- clusterK: if >0, prefilters neighbors using Euclidean k‑NN before hyperbolic checks; useful to reduce O(V^2) scans (default 0)
- autoThreshold: when true, the clustering threshold is estimated from a percentile of sampled pairwise hyperbolic distances (default false)
- autoThresholdPercentile: percentile in [0,1] used for threshold selection (default 0.35)
- autoThresholdSample: max number of pairs sampled to estimate the percentile (default 3000)
- autoThresholdMethod: percentile, mad, or hybrid. The mad method uses a robust lower-tail cutoff: `threshold = median - K * 1.4826 * MAD`. The hybrid method picks between percentile and MAD automatically based on outlieriness.
- autoThresholdMADK: K multiplier for MAD; higher K → lower threshold (more edges), default 0.5

Auto-threshold diagnostics (verbose): when `verbose: true` and `autoThreshold: true`, the analyzer logs extra stats about the sampled pairwise distance distribution: median, MAD, sigma≈1.4826·MAD, p95, the chosen method (percentile/mad/hybrid) and the effective threshold.

Diagnostics-only mode: set `diagnosticsOnly: true` to compute embeddings and distance statistics without clustering. Useful to tune thresholds and inspect distributions quickly. You can also enable a histogram via `autoThresholdHistogramBins`.

## What the algorithm does

1. Preprocess

- Lowercase, optional NFKC normalization
- Keep only letter sequences of length >= 2 (Unicode aware)

1. Co‑occurrence matrix (sparse)

- Sliding window of configurable size around each word
- Optional distance weighting inside the window
- Vocabulary capped by frequency to `maxVocab`

1. Heuristic hyperbolic embeddings

- Row values mapped to a small Euclidean vector via either:
  - firstD: normalized first D columns (legacy)
  - random: normalized sum over random column groups per dimension (more robust, seed‑controlled)
- Then projected into the Poincaré disk by radial scaling (r < 1)

SVD mode (optional): for small vocabularies (n <= svdMaxN), compute a dense SVD and take the first D left singular vectors scaled by singular values, then project into the Poincaré disk. Requires `ml-matrix` or `svd-js`; the code falls back automatically if unavailable.

1. Clustering (union‑find)

- Build an undirected graph connecting words whose hyperbolic distance is < threshold
- Extract connected components; each becomes a cluster
- This is order‑invariant and deterministic given the seed

Optional k‑NN prefilter: when `clusterK > 0`, compute Euclidean k‑nearest neighbors on embeddings and only check hyperbolic distances for those pairs. This reduces pairwise checks from O(V^2) to ~O(V*K) at the cost of a heuristic prefilter.

Auto‑tuned threshold (optional): when `autoThreshold` is enabled, a threshold is chosen from sampled pairwise hyperbolic distances.

- percentile method: pick the p‑th percentile (e.g., 0.35)
- mad method: robust cutoff using median and MAD: threshold = median − K·1.4826·MAD (e.g., K=0.5)
- hybrid method: choose MAD if the upper tail is far from center (using a simple rule with p95 and MAD); otherwise use percentile

1. Compression estimate

- Compressed size ≈ number of clusters + 50% of total membership as mapping overhead (toy model)
- Reports ratio and savings (%)

## Interpreting results

- Higher clusterThreshold → fewer, larger clusters → stronger “compression” but looser semantics
- Lower clusterThreshold → more, smaller clusters → weaker “compression” but tighter semantics
- Try toggling `weighting: 'distance'` to capture locality better
- Use `projection: 'random'` for more stable behavior on sparse rows; increase `randomFeaturesPerDim` for smoother signals

## Robustness and edge cases

- Empty/short inputs return zero clusters and a zeroed compression ratio
- Poincaré distance uses epsilon clamps to avoid numerical issues near the disk boundary
- Deterministic random generator (LCG) via `seed`
- Union‑find clustering avoids order bias of greedy scanning

## Embedded tests

Run the quick smoke tests:

```powershell
$env:HTC_RUN_TESTS='1'; node .\compressionTest.js; Remove-Item Env:HTC_RUN_TESTS
```

They cover tokenization, empty input handling, and determinism.

## Benchmark harness

There’s a very small benchmarking script `bench.js` that prints one JSON line per run. It helps compare projections, k values, and (optionally) auto‑threshold across one or more inputs.

Examples (PowerShell):

```powershell
# Single file, random projection, auto‑threshold at p=0.35
npm run bench -- --file .\sample.txt --auto --percentile 0.35

# Directory of .txt files, sweep projection and K
npm run bench -- --dir .\texts --projection random,svd --k 0,10 --auto --percentile 0.30 --sample 4000
```

MAD method example:

```powershell
# Use MAD-based auto-threshold with K=0.5
npm run bench -- --file .\sample.txt --auto --autoMethod mad --madK 0.5
```

Hybrid method example:

```powershell
# Hybrid auto threshold: lets the analyzer select between percentile and MAD per input
npm run bench -- --file .\sample.txt --auto --autoMethod hybrid --percentile 0.35 --madK 0.5
```

Emit auto-threshold diagnostics in JSON:

```powershell
# Add --autoStats to include an autoThresholdStats object in each JSON line
npm run bench -- --file .\\sample.txt --auto --autoMethod hybrid --autoStats
```

The `autoThresholdStats` object contains:

- sampleSize, usedAllPairs
- percentile (configured) and thresholdFromPercentile
- autoMethodConfigured and chosenMethod
- median, mad, sigma
- percentiles p10, p25, p50, p75, p90, p95, p99
- histogram: { bins, min, max, counts } when enabled

Compare percentile vs MAD:

```powershell
# Percentile-based auto threshold (p=0.35)
npm run bench -- --file .\sample.txt --auto --percentile 0.35

# MAD-based auto threshold (K=0.5)
npm run bench -- --file .\sample.txt --auto --autoMethod mad --madK 0.5
```

### Pretty report and HTML export

Run bench on the included sample and render a pretty table plus an HTML report:

```powershell
# Generate some data
npm run bench -- --file .\samples\sample.txt --auto --autoMethod hybrid --k 0,10 --approxKNN 1 --approxKCandidates 100 --emitClusters .\out\clusters --outJson .\out\bench.jsonl

# Print a console table and write ./out/report.html
npm run report
```

The HTML report is saved to `out\report.html`. Open it in a browser to show results with basic styling and savings bars.

Tips:

- To include per-run distance histograms, run bench with diagnostics enabled:
  - Add `--autoStats` and `--histBins N` (e.g., `--histBins 20`).
- The HTML report shows:
  - A results table for all runs in your JSONL
  - Summary charts by input (best savings% and clusters)
  - Savings% by K for each projection (averaged over runs with same K/projection)
  - Clusters count by K for each projection (averaged)
  - Grouped chart: savings% by K across projections (side-by-side grouped bars, averaged)
  - Auto-threshold diagnostics (median/MAD/sigma/percentiles) when available
  - Per-run distance histograms when available

Notes on charts:

- The K-by-projection charts aggregate multiple runs by taking the mean for each (projection, K) pair found in your JSONL. Run sweeps over multiple K values and projections to populate these views.
Notes:

- K controls how conservative the MAD cutoff is. The formula is `threshold = median - K * 1.4826 * MAD`.
  - Larger K lowers the threshold, creating fewer edges and smaller/stricter clusters.
  - Smaller K raises the threshold (relative to larger K), creating more edges and larger/looser clusters.
- On very small corpora, pairwise distances can collapse near zero. Auto-thresholds will then be tiny; this is expected. Prefer percentile on small samples, or increase vocabulary/window.
- For larger corpora with outliers, MAD tends to be more stable than a fixed percentile.

Suggested starting values:

- Very small corpora (≤ 200 unique words)
  - Percentile: p = 0.25–0.35
  - MAD: K = 0.20–0.40
  - Tip: distances may collapse; consider increasing window or vocabulary cap if clusters look trivial.
- Small/medium corpora (200–2000 unique words)
  - Percentile: p = 0.30–0.45
  - MAD: K = 0.40–0.70
  - Tip: if clusters are too big, lower p or raise K; if too fragmented, raise p or lower K.
- Large corpora (≥ 2000 unique words)
  - Percentile: p = 0.35–0.55
  - MAD: K = 0.50–0.90
  - Tip: if co-occurrence is dense (large window, distance weighting), lean toward the high end; if sparse, lean lower.

Choosing a method:

- Prefer percentile for small samples and quick sweeps.
- Prefer MAD when distance distributions have outliers or are skewed; it’s more robust and tends to stabilize results.
- Prefer hybrid when you don’t want to pick upfront; it will choose MAD on outlier-heavy inputs and fallback to percentile otherwise.

Auto‑threshold diagnostics cheat‑sheet:

- If p95 − median is much larger than sigma (e.g., > 3·sigma), distances are skewed with a heavy upper tail → MAD often yields more stable thresholds.
- If median and p95 are close relative to sigma, percentile tends to be fine and simpler to reason about.
- If thresholds come out extremely small (≈ 1e‑6), your corpus is tiny/sparse; switch to percentile with higher p or increase vocabulary/window.

### Troubleshooting thresholds

- Symptom: One giant cluster or very few clusters (over-merged)
  - Lower the threshold:
    - Percentile: decrease p (e.g., from 0.45 → 0.30)
    - MAD: increase K (e.g., from 0.4 → 0.7)
  - Optionally reduce `clusterK` to consider fewer neighbors in the prefilter
  - Consider a smaller `windowSize` or `weighting: 'distance'` to reduce co-occurrence density

- Symptom: Too many tiny clusters (over-fragmented)
  - Raise the threshold:
    - Percentile: increase p (e.g., from 0.30 → 0.45)
    - MAD: decrease K (e.g., from 0.7 → 0.4)
  - Optionally increase `clusterK` to consider more neighbors
  - Consider a larger `windowSize` or `weighting: 'uniform'`

- Symptom: Threshold is extremely small (e.g., ~1e-6) on tiny corpora
  - Prefer percentile with a higher p (e.g., 0.40–0.50)
  - Increase `autoThresholdSample` or set a fixed `clusterThreshold`
  - Increase `windowSize` and/or allow a larger `maxVocab` to enrich distances

- Symptom: Results vary too much across runs
  - Set a fixed `seed` and increase `randomFeaturesPerDim`
  - For small vocabularies, try `projection: 'svd'` for more stable embeddings

Quick adjustment examples (PowerShell):

```powershell
# If clusters are too few (over-merged)
npm run bench -- --file .\sample.txt --auto --percentile 0.30
npm run bench -- --file .\sample.txt --auto --autoMethod mad --madK 0.7

# If clusters are too many (over-fragmented)
npm run bench -- --file .\sample.txt --auto --percentile 0.45
npm run bench -- --file .\sample.txt --auto --autoMethod mad --madK 0.4
```

Common flags:

- --file path or --dir path: input(s)
- --projection random,firstD,svd
- --k list: e.g., 0,10,25
- --auto [--percentile p] [--sample N]
- --autoMethod mad|percentile and, if mad, --madK K
- --threshold x: fixed threshold (overrides auto)
- --weighting uniform|distance, --window n, --maxVocab n, --svdMaxN n
- --verbose 1 to enable per‑stage logs in the core analyzer
- --diagOnly to skip clustering and emit diagnostics
- --histBins N to include a histogram of sampled distances
- --approxKNN 1 and --approxKCandidates N to enable approximate k‑NN prefilter
- --dimensions d1,d2,... to sweep multiple embedding dimensions
- --emitClusters .\out\clusters to save clusters per run as JSON files
- --outJson .\out\bench.jsonl to append JSON lines to a file instead of stdout

## Performance tips

- Increase `maxVocab` cautiously: both co‑occurrence building and pairwise distances are O(V^2) in the worst case
- For longer texts, consider preprocessing to remove very rare words before the window pass
- If you need speed, lower `randomFeaturesPerDim` or switch to `projection: 'firstD'`
- For better quality with small vocabularies, try `projection: 'svd'`; ensure deps installed (see below)
- For large vocabularies, enable `clusterK` (e.g., 10–50) to avoid full O(V^2) clustering
- If clustering is still slow, set `approxKNN: true` with `approxKCandidates` (e.g., 100) to sample candidates per node and reduce prefilter cost deterministically (seeded)

## Installing optional SVD dependencies

If you plan to use `projection: 'svd'`, install dependencies in this folder:

```powershell
pnpm add ml-matrix svd-js cross-env
# or
npm install ml-matrix svd-js cross-env --save
# or
yarn add ml-matrix svd-js cross-env
```

Then you can run:

```powershell
npm run demo
npm test
```

## Research notes and next steps

See `hyperbolic_compression_analysis.md` and `ReportNonEUCompression.html` for broader context and visuals. Potential future improvements:

- Replace heuristic projection with Truncated SVD or randomized PCA before Poincaré projection
- Refine the existing k‑NN prefilter (already implemented) with approximate KNN for scalability
- Refine the existing auto‑thresholding (already implemented: percentile/MAD/hybrid) with class‑balance heuristics and multi‑modal modeling
- Streaming co‑occurrence builder for very large corpora
- Optional TF‑IDF reweighting of co‑occurrence counts

## License

This prototype intentionally avoids external dependencies and is provided as‑is for research and discussion.
