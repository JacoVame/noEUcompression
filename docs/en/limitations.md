# Limitations

← [Index](./README.md)

> A visual mind-map of these same limits is in [`docs/diagram/diagrams.md`](../diagram/diagrams.md).

The limitations below are **by design**, not bugs. Knowing what the prototype does not do is as important as knowing what it does.

## 1 · The compression is a toy

`ratio` does not compare bytes: it compares the **number of tokens** in the text against the **number of clusters + 50% of vocabulary** (overhead of a fictional mapping). It is a thermometer of semantic density, not a `.gz` label.

> A serious comparison would need an entropy coder (Huffman / arithmetic / ANS) using clusters as symbols. See [improvements](./improvements.md).

## 2 · No comparison with `gzip`/`brotli`/`zstd`

There is no benchmark measuring "bytes saved over gzip". The prototype is explicitly exploratory. The `savingsPct` figure **is not** comparable to real compressors.

## 3 · O(V²) computational cost

Pairwise distances on the Poincaré disk are expensive: 5000 words means 12.5 M pairs. The `clusterK` prefilter (Euclidean k-NN) brings cost down to O(V·K), and `approxKNN` further. Still a prototype, not a production system over millions of words.

> No streaming (the co-occurrence matrix lives entirely in memory). For very large corpora an incremental builder is needed.

## 4 · Parameter sensitivity

Key knobs (`windowSize`, `clusterThreshold`, `projection`, `randomFeaturesPerDim`) substantially affect results. `savingsPct` can swing by tens of points as the threshold moves. Without a fixed seed, reproducibility is incomplete.

> Auto-threshold (percentile / MAD / hybrid) mitigates this but does not erase it: small corpora yield poor distance samples and the auto-pick can land on a tiny threshold (≈ 1e-6).

## 5 · Small corpora behave poorly

Below ~200 unique words, the system struggles: distances collapse near zero, histograms become unimodal, auto-threshold degenerates. Documented in the project [`README.md`](../../README.md), and the reason for the percentile cheat-sheet in [parameters and CLI](./parameters-and-cli.md).

## 6 · Only one language is genuinely tested

All examples and smoke tests use Italian. Preprocessing is Unicode-aware, so it *should* work on other languages, but:

- No lemmatisation: "ran" and "running" are distinct words.
- No stop-words: articles and prepositions land in the giant cluster (see `out/clusters/sample.txt__d2__random__k0.clusters.json`).
- No morphological analysis.

## 7 · Optional dependencies for SVD

`projection: 'svd'` requires `ml-matrix` or `svd-js`. Without them the system silently falls back to `random`. Robust, but a user expecting "SVD quality" might never realise they did not get it.

## 8 · No decompressor

The pipeline is **one-way semantic compression**: text in, clusters and an estimate out. There is no inverse operation that, given the cluster dictionary, reconstructs the original text.

> A lossless decompressor would need at least: a word→cluster-ID mapping, a coder that stores the ID sequence, and a canonical extractor for each cluster. All of this is sketched in [improvements](./improvements.md).

## 9 · Representative = first index

The cluster representative is the first word that lands inside it. Deterministic but **not semantically meaningful**: fine for a teaching tool; for a synthesis system the *medoid* (the most central word) would be a better choice.

## 10 · Real numbers from `bench.jsonl`

On `samples/sample.txt` (Italian, 65 unique words):

- 3 clusters — one large (63 words), two singletons.
- Auto-threshold = 0.51 (`percentile` chosen by the hybrid rule).
- `savingsPct` = 54.5%, but… see point 1: it is a thermometer.

Read another way: three semantic families emerge but two are too small to be useful. Exactly what to expect from a five-line paragraph: the prototype behaves honestly.

## Continue

➡️ [Use cases: where it actually makes sense](./use-cases.md)
