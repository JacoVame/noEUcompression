# Parameters and CLI

← [Index](./README.md)

Every knob available to experimenters. For surgical detail keep the project [`README.md`](../../README.md) open: this page summarises and groups it.

## Install

```bash
git clone <repo>
cd noEUcompression
# no required dependencies
node ./compressionTest.js
```

For SVD projection (optional):

```bash
npm install ml-matrix svd-js cross-env --save
# or: pnpm add ml-matrix svd-js cross-env
```

## `npm` scripts

| Command | What it does |
|---------|--------------|
| `npm run demo` | Runs the prototype on a built-in Italian paragraph. |
| `npm test` | Runs the embedded smoke tests. |
| `npm run bench` | Launches the benchmark (see below). |
| `npm run report` | Generates an HTML report at `out/report.html` from `out/bench.jsonl`. |

## Constructor (programmatic use)

```js
const HyperbolicTextCompressor = require('./compressionTest');

const c = new HyperbolicTextCompressor(2 /* dimension */, {
  maxVocab: 3000,
  seed: 42,
  windowSize: 3,
  clusterThreshold: 0.4,
  projection: 'random',          // 'random' | 'firstD' | 'svd'
  randomFeaturesPerDim: 16,
  weighting: 'distance',         // 'uniform' | 'distance'
  normalize: true,
  verbose: true,
  svdMaxN: 800,
  clusterK: 0,
  approxKNN: false,
  approxKCandidates: 50,
  autoThreshold: true,
  autoThresholdPercentile: 0.35,
  autoThresholdSample: 3000,
  autoThresholdMethod: 'hybrid', // 'percentile' | 'mad' | 'hybrid'
  autoThresholdMADK: 0.5,
  autoThresholdHistogramBins: 20,
  diagnosticsOnly: false
});

const r = c.analyzeAndCompress(text);
console.log(r.compressionRatio, r.clusters.length);
```

### Knobs that matter

| Option | What it controls | When to touch |
|---|---|---|
| `dimension` | Embedding axes (default 2) | 2 to plot; 3–8 for quality |
| `windowSize` | Co-occurrence window radius | Wider ⇒ broader context |
| `clusterThreshold` | Manual distance threshold | When auto-threshold is off |
| `projection` | Reduction strategy | `random` for stability; `svd` for quality on small corpora |
| `clusterK` | k-NN prefilter | On large vocab (V > 1000) |
| `autoThreshold` | Auto-pick threshold | Almost always worthwhile |
| `autoThresholdMethod` | Auto strategy | `hybrid` if undecided |
| `seed` | Reproducibility | Always for serious benchmarks |

## Benchmark CLI

`bench.js` prints one JSON line per run. Ideal for parameter sweeps.

### Practical examples

```bash
# Single file, hybrid auto-threshold, full diagnostics
npm run bench -- --file ./samples/sample.txt --auto --autoMethod hybrid --autoStats

# Sweep dimensions, projections, k-NN
npm run bench -- --file ./samples/sample.txt \
  --dimensions 2,3 --projection random,svd --k 0,10,25 \
  --auto --outJson ./out/bench.jsonl

# Save clusters JSON + render HTML report
npm run bench -- --file ./samples/sample.txt --auto --autoMethod hybrid \
  --autoStats --emitClusters ./out/clusters --outJson ./out/bench.jsonl
npm run report
```

### All flags

| Flag | Description |
|------|-------------|
| `--file PATH` | Single text file |
| `--dir PATH` | Directory of `.txt` files |
| `--dimension N` | Embedding dimensions |
| `--dimensions a,b,c` | Sweep multiple dimensions |
| `--projection x,y` | `random`, `firstD`, `svd` (multi) |
| `--k a,b,c` | k-NN values to try |
| `--threshold X` | Fixed threshold (overrides auto) |
| `--auto` | Enable auto-threshold |
| `--autoMethod m` | `percentile` · `mad` · `hybrid` |
| `--percentile p` | Percentile for `percentile`/`hybrid` |
| `--madK K` | Constant for the MAD method |
| `--sample N` | Max sampled pairs |
| `--autoStats` | Emit diagnostics in JSON |
| `--diagOnly` | Skip clustering, diagnostics only |
| `--histBins N` | Histogram of distances |
| `--approxKNN 0\|1` | Enable approximate k-NN |
| `--approxKCandidates N` | Candidates per node |
| `--emitClusters PATH` | Save clusters per run |
| `--outJson PATH` | JSONL instead of stdout |
| `--weighting w` | `uniform` · `distance` |
| `--window N` | Co-occurrence window radius |
| `--maxVocab N` | Vocabulary cap |
| `--seed N` | RNG seed |
| `--svdMaxN N` | Max vocab for SVD |
| `--normalize 0\|1` | NFKC on/off |
| `--verbose 0\|1` | Verbose logs |

## What you get from a benchmark

Real example from `out/bench.jsonl` (run on `samples/sample.txt`):

```json
{
  "input": "sample.txt",
  "dimension": 2,
  "projection": "random",
  "clusterK": 0,
  "autoThreshold": true,
  "clusterThresholdUsed": 0.5097,
  "uniqueWords": 65,
  "clusters": 3,
  "ratio": 0.4551,
  "savingsPct": "54.5",
  "timingsMs": { "preprocessMs": 1, "coocMs": 7, "embedMs": 1, "clusterMs": 3, "totalMs": 13 },
  "autoThresholdStats": {
    "sampleSize": 2080, "percentile": 0.35, "chosenMethod": "percentile",
    "median": 0.6803, "mad": 0.2607, "sigma": 0.3866,
    "p10": 0.2727, "p50": 0.6803, "p95": 1.4910,
    "histogram": { "bins": 20, "min": 0, "max": 2.3979, "counts": [/*...*/] }
  }
}
```

The HTML report (`npm run report` → `out/report.html`) gives tables, bar charts, histograms, and K-vs-projection comparisons.

## Quick threshold cheat-sheet

| Corpus size | Suggested percentile | MAD K |
|---|---|---|
| ≤ 200 unique words | 0.25–0.35 | 0.20–0.40 |
| 200–2000 | 0.30–0.45 | 0.40–0.70 |
| ≥ 2000 | 0.35–0.55 | 0.50–0.90 |

If clusters are **too few** (one giant): lower the percentile or raise K.
If clusters are **too many tiny ones**: raise the percentile or lower K.
If the threshold lands at `1e-6`: the corpus is too small — try a higher percentile or grow `windowSize`/`maxVocab`.

## Continue

➡️ [What the prototype does not do: honest limits](./limitations.md)
