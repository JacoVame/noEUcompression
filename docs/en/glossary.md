# Glossary

← [Index](./README.md)

Technical terms used in the project, translated into plain words.

| Term | Plain meaning |
|------|---------------|
| **NFKC** | A Unicode normalisation form that aligns diacritics, ligatures, and typographic variants. Makes "café" and "café" the same word. |
| **Tokenisation** | Splitting the text into words. Here we keep only Unicode letter sequences of length ≥ 2. |
| **Co-occurrence** | How often two words appear close to each other within a sliding window. A measure of "shared context". |
| **Sparse matrix** | A matrix where most cells are zero, so we store only non-zero ones. Memory savings, slower access. |
| **Embedding** | A numerical (vector) representation of a word, supposed to capture meaning. The closer two words' meanings, the closer their vectors should be. |
| **Random projection** | A technique to reduce vector dimension by projecting onto a few random directions. Fast, simple, surprisingly effective. |
| **SVD (Singular Value Decomposition)** | A matrix factorisation finding the "most important" directions. Core of many dimensionality-reduction techniques. |
| **Poincaré disk** | A model of hyperbolic geometry living inside a circle of radius 1. From outside it looks finite; from inside the boundary is infinitely far. |
| **Hyperbolic geometry** | A geometry of constant negative curvature. Volume grows exponentially with distance from the centre: ideal for trees. |
| **Möbius distance** | The "true" distance inside the Poincaré disk: `acosh(1 + 2‖u−v‖² / ((1−‖u‖²)(1−‖v‖²)))`. |
| **Cluster** | A group of words considered similar by the system. |
| **Union-find** | A data structure for tracking groups of elements and merging them quickly. Used here to extract clusters as connected components of a graph. |
| **Connected component** | In a graph, a subset of nodes all reachable from one another. |
| **k-NN (k-nearest neighbours)** | Finding the k closest points to a given one. Used here as a prefilter: if two words are not among the k Euclidean neighbours, we do not bother computing the hyperbolic distance. |
| **Threshold** | A cutoff above which two words are *not* linked. Decides how "wide" clusters are. |
| **MAD (Median Absolute Deviation)** | A robust dispersion measure: the median of the absolute deviations from the median. Resists outliers. |
| **Percentile** | The value below which a given percentage of data falls. The 35th percentile is the value below which 35% of samples lie. |
| **σ (sigma)** | Here, an estimate of standard deviation derived from MAD (`σ ≈ 1.4826 · MAD`). |
| **LCG (Linear Congruential Generator)** | A simple pseudo-random number generator, deterministic given a seed. Used for reproducibility. |
| **Determinism** | Same run, same input, same output — every time. Holds here given a fixed `seed`. |
| **ratio** | The prototype's compression index: `compressed / original`. Smaller means more "savings". |
| **savingsPct** | `(1 − ratio) · 100`. Estimated percentage savings. |
| **Toy model** | A simplified model useful for reasoning, not for production. |

## Continue

➡️ [Frequently asked questions](./faq.md)
