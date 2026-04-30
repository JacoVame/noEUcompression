# Improvements

← [Index](./README.md)

> Visual version: see [`docs/diagram/diagrams.md`](../diagram/diagrams.md).

An honest roadmap of what would turn the prototype into something more useful. Each entry is a real challenge, not a polish detail.

## A. Toward real compression

### A1. Entropy coding

Today the compression is an estimate. To make it **real**:

1. Encode every word in the text as a cluster ID (smaller than the original symbol).
2. Run an entropy coder (Huffman / arithmetic / ANS) over the ID sequence.
3. Add the size of the mapping table.

Expected result: measurable bytes, comparable to `gzip`.

### A2. Decompressor

To rebuild text from the compressed stream, every cluster needs a *canonical representative* (today's "first index" is too arbitrary). The decompressor then replaces each ID with the chosen word. Compression becomes **lossy** with respect to the original text, but is *invertible up to a dictionary*.

### A3. Comparison with standard baselines

A script that, given the same file, reports:

- original bytes
- gzip bytes
- brotli bytes
- zstd bytes
- bytes estimated by the prototype (with a real encoder)

closing the empirical loop.

## B. Scalability

### B1. Streaming co-occurrence builder

Today everything lives in memory. For long texts:

- Block-wise reading.
- Incremental update of the sparse matrix.
- Optional disk spilling (LMDB, SQLite, JSONL).

### B2. Truncated SVD / randomized PCA

`projection: 'svd'` currently does a full dense SVD (and does not scale). **Truncated SVD** or **randomized PCA** would handle vocabularies of tens of thousands of words with bounded memory.

### B3. Approximate hyperbolic k-NN

Today's `approxKNN` is deterministic candidate sampling. Structures like **HNSW** or **IVF** could drastically reduce the cost of finding hyperbolic neighbours while preserving quality.

### B4. GPU / WebAssembly acceleration

Pairwise distances are GPU-friendly. A WebAssembly build would run the whole thing in a browser, dependency-free.

## C. Semantic quality

### C1. TF-IDF / PMI re-weighting

Raw co-occurrence over-weights frequent words. **TF-IDF** or **PPMI (Positive Pointwise Mutual Information)** gives more voice to rare-but-informative words.

### C2. Trained embeddings

Replace projection + scaling with a **trained hyperbolic embedding** (Poincaré GloVe, hyperbolic Word2Vec, hyperbolic transformers). A significant jump in quality — and in dependencies.

### C3. Multilingual validation

Test suite over corpora in English, German, Chinese, Arabic. Measure how often the system finds sensible clusters (e.g. against known gold-standard clusters).

### C4. Semantic representatives

Replace "first index" with the cluster's **medoid** (the word with minimal sum of hyperbolic distances to others). The representative also becomes a good cluster summary for the decompressor.

## D. Quality of life

- Python bindings (for comparison against scikit-learn / numpy).
- Jupyter notebook plugin with interactive disk visualisation.
- Non-regression tests that pin expected clusters on `samples/sample.txt`.
- A `--watch` mode for benchmarks.

## Contributing

Issues and PRs are welcome. Ideas, reports, experiments: opening a *discussion* on GitHub is the simplest path.

## Continue

➡️ [Glossary](./glossary.md)
