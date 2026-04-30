# Overview

← [Index](./README.md)

## What it is (one sentence)

`HyperbolicTextCompressor` is a tiny JavaScript prototype that takes text, maps the words into a curved space (the Poincaré disk), groups them into semantic families and reports a *compression ratio* that gauges how much redundancy those families absorbed.

## Why "hyperbolic"?

Schoolbook geometry is Euclidean: straight lines, triangle angles summing to 180°, distances that compose predictably. It is great for a sheet of paper or a football pitch.

Language is not flat: it has hierarchies, trees of meaning, parent words and children. Tree-shaped data fits naturally inside a hyperbolic space because the available volume grows *exponentially* with the distance from the centre — exactly as the number of nodes grows level by level in a tree.

In flat space words step on each other's toes; in curved space there is room to organise the families with a bit of breathing space.

## Why "non-EU"?

"Non-EU" in the project name is a joke. It stands for *non-Euclidean*. Nothing to do with European regulations or data rules. Geometry only.

## Who is this for

- **Curious readers** who want a feel for how mathematics can represent meaning, without becoming mathematicians.
- **Students and teachers**: the code is readable, deterministic, with no required dependencies. It is well-suited to lessons on sparse matrices, union-find, embeddings, and visualisation.
- **Researchers** who want to experiment with simple Euclidean projections before reaching for trained embeddings such as Poincaré GloVe.
- **NLP-curious developers** who do not want to download a multi-gigabyte model just to see reasonable clusters on a single paragraph.

## Who this is **not** for

- It is not a substitute for `gzip`, `brotli`, or `zstd`. The "compression" here is a toy estimate based on the number of clusters: it gauges semantic quality, not byte-level shrinkage.
- There is no decompressor: the mapping is not lossless-invertible.
- It is not optimised for production: benchmarks are O(V²) on the vocabulary.

## What is different from a classical compressor

Traditional compressors (LZ77, Huffman, arithmetic coding) chase *syntactic* patterns: repeated strings, frequent symbols receiving shorter codes. They work beautifully but they do not "understand" what the words mean.

The idea here is the opposite: chase *semantic* patterns. Two words are "similar" if they appear near the same other words. Group them into clusters, and use the cluster as a summary of their meaning. The result is not a smaller file; it is a smaller dictionary — a kind of *vocabulary compression*.

## Project status

- **Version**: 0.1.0 (prototype).
- **Language**: JavaScript (Node.js 16+).
- **Required dependencies**: none.
- **Optional dependencies**: `ml-matrix` or `svd-js` (only for SVD projection).
- **Tests**: smoke tests embedded in the main module (`HTC_RUN_TESTS=1 node compressionTest.js`).
- **Determinism**: complete, given a seed.
- **License**: MIT.

## Continue

➡️ [The eight-step pipeline](./pipeline.md)
