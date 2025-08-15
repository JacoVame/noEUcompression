# Text Compression via Non‑Euclidean Geometries

## Abstract

This document presents an exploratory approach to text compression based on representing texts in non‑Euclidean geometric spaces, with particular focus on hyperbolic spaces (Poincaré disk model). The research hypothesis is that non‑Euclidean geometries can capture deep semantic and syntactic structures of natural language more effectively than traditional approaches, potentially enabling higher compression ratios.

---

## 1. Motivation and Theoretical Context

### 1.1 Limitations of Classical Approaches

Traditional text compression methods (LZ77, arithmetic coding, transformer‑based) mainly operate on:

- Character patterns and sequences
- Statistical frequencies
- Surface‑level syntactic structures

However, these approaches do not fully exploit the deep semantic relationships and hierarchical structures inherent in natural language.

### 1.2 Potential of Non‑Euclidean Geometries

Non‑Euclidean geometries offer unique properties for language representation:

**Hyperbolic Spaces:**

- Exponential volume growth → natural for hierarchical structures
- Geodesic distances → optimal semantic paths
- Already used successfully in linguistic embeddings (Poincaré embeddings)

**Other Candidate Geometries:**

- **Riemannian manifolds**: variable curvature for different semantic domains
- **Tori**: periodic structures for recurring patterns
- **Simplicial complexes**: n‑ary relations among concepts
- **Projective spaces**: duality for complementary relations

---

## 2. Proposed Approach

### 2.1 Compression Pipeline

```text
Original Text
      ↓
1. Preprocessing (tokenization, normalization)
      ↓
2. Co‑occurrence Analysis (sliding window)
      ↓
3. Co‑occurrence Matrix Construction
      ↓
4. Dimensionality Reduction / Projection (Random aggregation, SVD for small n)
    ↓
5. Mapping to Hyperbolic Space (Poincaré Disk)
    ↓
6. Semantic Clustering (hyperbolic distances; optional Euclidean k‑NN prefilter)
      ↓
7. Automatic Threshold Selection (percentile / MAD / hybrid) + Diagnostics
    ↓
8. Compression via Cluster Representatives
      ↓
Compressed Text + Decoding Tables + Statistics
```

### 2.2 Mathematical Foundations

#### Poincaré Disk Model

The Poincaré disk D = {z ∈ ℂ : |z| < 1} with metric:

```text
ds² = 4|dz|² / (1 - |z|²)²
```

#### Hyperbolic Distance

For two points u, v in the disk:

```text
d_H(u,v) = arccosh(1 + 2||u-v||²/((1-||u||²)(1-||v||²)))
```

#### Euclidean → Poincaré Mapping

Given a Euclidean vector x:

```text
x_poincaré = x · min(0.9/||x||, 1)
```

---

## 3. Prototype Implementation

### 3.1 System Architecture

```javascript
class HyperbolicTextCompressor {
    constructor(dimension = 2)
    
    // Core methods
    preprocessText(text)                    // Tokenization and cleaning
    createCooccurrenceMatrix(words)         // Co‑occurrence analysis
    embedInHyperbolic(matrix)               // Projection (random/firstD/SVD) + hyperbolic mapping
    poincareDistance(u, v)                  // Distance computation
    findSemanticClusters(threshold)         // Semantic clustering (union–find; optional k‑NN prefilter)
    _autoTuneThreshold(embeddings)          // Auto‑adaptive threshold (percentile/MAD/hybrid) with diagnostics
    estimateCompression(words, clusters)    // Compression estimate (toy model)
}
```

### 3.2 Semantic Clustering Algorithm

1. Initialization: each word is a singleton cluster
2. Distance computation: Poincaré hyperbolic distance
3. Merge: join clusters with distance < threshold
4. Representatives: choose a central word per cluster

Optional: Euclidean k‑NN prefilter on embeddings to reduce hyperbolic pair checks (from O(V²) to ~O(V·K)).

### 3.3 Compression Strategy

- Cluster Representatives: one representative word per cluster
- Mapping Table: cluster indices → original words
- Encoding: sequence of representatives + decoding tables

### 3.4 Key Options and Parameters (current prototype)

- Projection/Embedding: `projection: 'random' | 'firstD' | 'svd'` (SVD active only for small vocabularies, optional deps)
- Tokenization: Unicode‑aware with optional NFKC normalization
- Co‑occurrence matrix: configurable window; weights uniform or decaying with distance
- Clustering: union–find on hyperbolic distance threshold; optional Euclidean k‑NN prefilter (`clusterK`). For larger vocabularies, an approximate prefilter is available: `approxKNN: true` with `approxKCandidates` to sample deterministic candidates per node (seed‑controlled).
- Auto‑adaptive threshold: `autoThreshold` with methods `percentile`, `mad` (median ± MAD), or `hybrid` (automatic selection)
- Diagnostics: median, MAD, sigma ≈ 1.4826·MAD, p95, chosen method, sample size
- Benchmark: harness that emits JSON lines for repeatable comparisons over text sets

### 3.5 Auto‑Threshold and Diagnostics

- Percentile: threshold = p‑th percentile of sampled distances
- MAD (robust): threshold = median − K·1.4826·MAD (lower‑tail cutoff)
- Hybrid: automatically chooses between percentile and MAD using a simple criterion on upper‑tail asymmetry (p95 vs median and MAD)

For each estimate, the system logs summary stats useful for tuning and debugging (median, MAD, sigma, p95, chosen method, sample size used).

---

## 4. Experimental Results

### 4.1 Qualitative Observations

On the demo paragraph included in the code, one typically observes a few major clusters and several small ones. The toy compression ratio varies significantly with:

- Projection strategy (random/firstD/SVD)
- Window size and weighting scheme (uniform/distance)
- Threshold method and parameters (fixed or auto: percentile/MAD/hybrid)
- `clusterK` parameter for k‑NN prefilter
- PRNG seed and space dimensionality

For concrete numbers, use the `bench.js` tool which emits JSON lines with statistics and (optionally) threshold diagnostics. We avoid absolute values here to prevent out‑of‑context comparisons.

### 4.2 Reporting and Visualizations

To facilitate comparisons across configurations, a reporting script reads the JSONL produced by `bench.js` and generates an HTML file (`out/report.html`) with:

- Summary table of all runs
- Summary charts per input (best savings% and number of clusters)
- Savings% by K for each projection (averages over runs with the same K/projection)
- Number of clusters by K for each projection (averages)
- Grouped chart: savings% by K comparing projections (side‑by‑side bars)
- If available, histograms of sampled distances per run and a diagnostics section (median, MAD, sigma, percentiles, chosen method)

To obtain histograms, run the bench with `--autoStats` and `--histBins N`.

---

## 5. Comparison with Existing Approaches

### 5.1 Theoretical Advantages

| Aspect | Traditional Methods | Non‑Euclidean Geometries |
|--------|----------------------|--------------------------|
| **Semantics** | Limited to syntactic patterns | Captures deep semantic relationships |
| **Hierarchies** | Hard to represent | Natural in hyperbolic spaces |
| **Clustering** | Frequency‑based | Geometry‑based distances |
| **Scalability** | Linear/quadratic | O(V·K) with k‑NN prefilter |

### 5.2 Identified Limitations

- Computational overhead: hyperbolic distance calculations
- Critical parameters: clustering thresholds, space dimensionality
- Short texts: limited benefit vs overhead
- Limited validation: needs tests on larger corpora

---

## 6. Future Work

### 6.1 Immediate Improvements

**Algorithmic Optimization:**

- More efficient hyperbolic distance computations
- Incremental clustering algorithms
- Parallelization of embedding computations

**Adaptive Parameters:**

- Auto‑tuning of clustering thresholds (already in prototype: percentile/MAD/hybrid)
- Automatic dimensionality selection
- Co‑occurrence window optimization

### 6.2 Architectural Expansions

**Alternative Geometries:**

- Experiments with tori for cyclic patterns
- Riemann surfaces for multi‑topic texts
- Combining multiple geometries

**Hybrid Compression:**

- Integration with traditional compressors
- Pre/post‑processing with statistical methods
- Adaptive compression based on text type

### 6.3 Empirical Validation

**Systematic Benchmarks:**

- Comparison with gzip, bzip2, xz
- Tests on standard linguistic corpora
- Performance/quality trade‑off analysis

**Evaluation Metrics:**

- Absolute compression ratio
- Compression/decompression speed
- Semantic quality of reconstruction

---

## 7. Reference Implementation

### 7.1 Prototype Code

Note: the complete, up‑to‑date code is available in `compressionTest.js`. Below is a usage example with key options.

### 7.2 Usage Example

```javascript
const HyperbolicTextCompressor = require('./compressionTest');

const compressor = new HyperbolicTextCompressor(2, {
    seed: 42,
    projection: 'random',      // 'random' | 'firstD' | 'svd' (for small n)
    windowSize: 3,
    weighting: 'uniform',      // or 'distance'
    clusterK: 0,               // k‑NN prefilter: 0 disabled
    autoThreshold: true,
    autoThresholdMethod: 'hybrid', // 'percentile' | 'mad' | 'hybrid'
    autoThresholdPercentile: 0.35,
    autoThresholdMADK: 0.5,
    verbose: true
});

const text = 'Hyperbolic geometry offers new perspectives...';
const results = compressor.analyzeAndCompress(text);
console.log(results.autoThresholdStats); // threshold diagnostics
console.log(results.compressionRatio);
```

For systematic comparisons and repeatable measurements, use the `bench.js` tool which produces JSON lines with timings, thresholds, cluster stats, and (if requested) auto‑threshold diagnostics.

### 7.3 How to Run

- Quick demo:

    ```powershell
    npm run demo
    ```

- Embedded tests (smoke):

    ```powershell
    $env:HTC_RUN_TESTS='1'; node .\compressionTest.js; Remove-Item Env:HTC_RUN_TESTS
    ```

- Benchmark on a single file with hybrid auto‑threshold and diagnostics:

    ```powershell
    npm run bench -- --file .\sample.txt --auto --autoMethod hybrid --autoStats
    ```

---

## 8. Conclusions

### 8.1 Main Contributions

1. Innovative approach: exploratory use of non‑Euclidean geometries for semantic compression
2. Proof of concept: working implementation with auto‑thresholds (percentile/MAD/hybrid), diagnostics, and benchmarks
3. Extensible framework: modular architecture for testing different projections and parameters

### 8.2 Potential Impact

- Semantic compression: a paradigm beyond syntactic patterns
- NLP applications: improvements for embeddings and text representations
- Theoretical foundations: linking differential geometry and computational linguistics

### 8.3 Next Critical Steps

1. Large‑scale validation: tests on diverse corpora
2. Performance optimization: reducing computational overhead  
3. Empirical comparison: systematic benchmarks with standard compressors
4. Theoretical extension: rigorous mathematical formalization

---

## 9. References

### 9.1 Theoretical Foundations

- Hyperbolic Geometry: Cannon, J.W. "The geometric topology of 3-manifolds"
- Poincaré Embeddings: Nickel, M. & Kiela, D. "Poincaré Embeddings for Learning Hierarchical Representations"
- Non‑Euclidean Geometries in NLP: De Sa, C. et al. "Representation Tradeoffs for Hyperbolic Embeddings"

### 9.2 Text Compression

- Classical Algorithms: Salomon, D. "Data Compression: The Complete Reference"
- Statistical Methods: MacKay, D. "Information Theory, Inference and Learning Algorithms"
- Semantic Compression: Bengio, Y. et al. "Neural Language Models and Representation Learning"

### 9.3 Implementations and Code

- GitHub repository: [to be created for complete code]
- Test data: [to specify corpora used]
- Benchmarks: [to define standard test suite]

---

## Appendices

### Appendix A: Implementation Details

```javascript
// Optimal configuration parameters identified
const CONFIG = {
    dimension: 2,                    // Hyperbolic space dimensionality
    windowSize: 3,                   // Co‑occurrence window
    clusterThreshold: 0.4,           // Semantic clustering threshold
    poincareScale: 0.85              // Poincaré disk scaling factor
};
```

### Appendix B: Notes on Results

Results depend strongly on parameters and the nature of the text. Always report: projection, window, weights, auto‑threshold method/parameters, `clusterK` value, seed, and dimensionality.

### Appendix C: Complete Code

[The complete JavaScript prototype is available in the associated repository]

---

*Document prepared for collegial review – Version 1.0*  
*Date: August 2025*  
*Author: Gianluca Gagliano*
