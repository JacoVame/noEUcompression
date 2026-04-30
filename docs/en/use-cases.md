# Use cases

← [Index](./README.md)

> Visual version: see [`docs/diagram/diagrams.md`](../diagram/diagrams.md).

The prototype is not a file compressor. It is a **small laboratory** of hyperbolic geometry for text. Here is where it makes sense.

## 1 · Exploratory research

- **Hyperbolic geometry for language**: do you want to test whether negative curvature really captures word hierarchies? This is a minimal, deterministic, readable starting point.
- **Comparison against trained embeddings** (Poincaré GloVe, Hyperbolic Word2Vec): the Euclidean projection + scaling used here is faster, but obviously less informed. Useful as a baseline.
- **Adaptive threshold effects** (percentile / MAD / hybrid): the module is designed to measure the effect of these choices and includes full diagnostics.

## 2 · Teaching

- **Data-structures lessons**: the clustering section is a surgical example of union-find with path compression. Great for students who want a real-world feel.
- **Sparse matrices**: the `Map<column, count>` per row representation is readable in dozens of lines.
- **Visualising the Poincaré disk**: the animated pipeline at `docs/diagram/pipeline.html` conveys the idea without requiring differential geometry knowledge.

## 3 · Exploratory NLP

- **Finding word families**: on a small enough text, the system identifies reasonable clusters without a pre-trained model.
- **Vocabulary summarisation**: useful for dataset hygiene (which words are functional, which rare topical words).
- **De-facto stop-words**: the giant central cluster typically contains articles and prepositions.

## 4 · Pipeline benchmarking

- **Parameter sweeps**: `bench.js` is built to iterate over `dimension`, `projection`, `clusterK`, auto-threshold method, and produces JSONL ready for downstream analysis.
- **Prefilter strategy comparison**: full O(V²) vs exact k-NN vs approximate k-NN. Per-stage timings (`timingsMs`) are reported.
- **Distance-distribution diagnostics**: with `--autoStats --histBins 20` you get a small dashboard of the distribution. Useful to understand why auto-threshold chose what it chose.

## 5 · Sandbox for new projectors

The module isolates the three phases (reduction, hyperbolic scaling, distance) cleanly enough to serve as a playground for:

- New projection strategies (truncated SVD, randomized PCA, sparse projections).
- New disk metrics (Lorentz, half-space, approximate distances).
- Hybrid embeddings (partly Euclidean, partly hyperbolic).

## When *not* to use it

- If you need smaller files on the wire: use `gzip`/`brotli`/`zstd`.
- If you need to understand a sentence: use a real language model.
- If you need to handle million-word vocabularies in production: O(V²) will hurt.

## Continue

➡️ [Improvement roadmap](./improvements.md)
