<!-- ENGLISH · slide source for reveal.js (markdown plugin). Separator: ---, vertical: -- -->

<!-- .slide: class="title" -->
# HyperbolicTextCompressor
## Compressing meaning, not bytes
<div class="author">Gianluca Gagliano · acknowledgments to Vito Di Gesù and Domenico Tegolo</div>
<div class="muted small">A ~30-minute talk · ENGLISH</div>

---

## The opening question

> "Can I *compress* a text not by shortening symbols, but by gathering similar words?"

<span class="pill">non-EU</span> *non-Euclidean*, not "non-European". Geometry, not policy.

note:
Soft opener. Spell the name out immediately or someone will think it's about EU regulations. The leap is from *syntactic* compression (Huffman, LZ) to *semantic* compression.

---

## Where the idea comes from

- Words take meaning from their **neighbours**.
- Vocabularies are **trees**: "animal → mammal → dog → labrador".
- For trees, hyperbolic geometry beats Euclidean.

note:
Use the metaphor: "people in a small town who recognise each other through the streets they walk". Cite Nickel & Kiela 2017.

---

## Flat space vs curved space

<div class="columns">
<div>

**Flat (Euclidean)**
- Volume grows as *r^d*
- Unique parallel lines
- Triangles sum to 180°

</div>
<div>

**Curved (hyperbolic)**
- Volume grows **exponentially**
- Infinitely many parallels
- Triangles look "thinner"

</div>
</div>

note:
Exponential volume growth is the headline: trees need infinite room. Mention Escher's shrinking fish.

---

## The Poincaré disk

<img src="../shared/pipeline.svg" alt="Pipeline" style="max-width: 95%;"/>

note:
Show the pipeline up front so the audience sees the destination. Below, the disk has an infinite boundary.

---

## In one slide: what the prototype does

1. **Cleans** the text
2. **Counts** who appears near whom
3. **Reduces** each word to a small vector
4. **Pushes** vectors into the Poincaré disk
5. **Measures** hyperbolic distances
6. **Picks** a threshold by itself
7. **Groups** into clusters
8. **Estimates** a compression index

note:
Eight steps. Keep the list mental for the next slides; we'll revisit it.

---

## See it run (animated)

<iframe class="pipeline-frame" src="../../docs/diagram/pipeline.html" loading="lazy"></iframe>

note:
Open the interactive page inside an iframe. One full loop before zooming in.

---

## 1 · Preprocess

```text
"Gregor Samsa awoke one morning..."
↓ NFKC normalize
↓ /\p{L}{2,}/gu
[gregor, samsa, awoke, one, morning, ...]
```

- NFKC: aligns diacritics and typographic variants
- Letter sequences ≥ 2

note:
Looks trivial but it is the most important filter. Without cleaning, downstream is noise.

---

## 2 · Co-occurrence

<div class="columns">
<div>

- Sliding window `windowSize` (default 3)
- Count every pair within the window
- Weighted (`uniform` or `1/(1+|i−j|)`)

</div>
<div>

```js
// sparse matrix
row[wordIdx] = Map<colIdx, count>;
// vocab cap maxVocab
```

</div>
</div>

note:
Highlight sparsity. On `sample.txt`: 65 unique words, ~150 pairs with count > 0.

---

## 3 · Embedding (reduction)

| Strategy | When |
|----------|------|
| `random` | Default, robust, sparse-OK |
| `firstD` | Legacy, reproducible |
| `svd` | Small vocab, quality (opt deps) |

```js
new HyperbolicTextCompressor(2, { projection: 'random', randomFeaturesPerDim: 16 })
```

note:
Random projection is surprisingly effective. Cite Johnson-Lindenstrauss for theory.

---

## 4 · Poincaré disk

```
x_poincaré = x · min(0.85 / ‖x‖, 1.0)
```

<span class="pill">constraint</span> `‖x‖ < 1` — always inside the disk
<span class="pill">margin</span> 0.85 — kept away from the boundary

note:
Radial scaling is trivial. The 0.85 factor avoids singularities of the metric.

---

## 5 · Hyperbolic distance (Möbius)

```
d_H(u,v) = acosh(1 + 2·‖u−v‖² / ((1−‖u‖²)(1−‖v‖²)))
```

- Near the centre: ≈ Euclidean
- Near the boundary: **explodes**

note:
The formula is dramatic but the message is simple: the metric amplifies differences toward the boundary. That is what separates semantic families.

---

## 6 · Auto-threshold: the system decides

| Method | Idea | When |
|--------|------|------|
| `percentile` | p35 of a sample | Regular distributions |
| `mad` | `median − K·1.4826·MAD` | Outliers present |
| `hybrid` | picks automatically | Recommended default |

note:
Point: no magic numbers to tune. The system inspects the distribution and decides.

---

## 6 · Threshold dashboard (real example)

On `samples/sample.txt`:

| Statistic | Value |
|-----------|-------|
| Sample size | 2080 pairs |
| Median | 0.680 |
| MAD | 0.261 |
| σ ≈ 1.4826·MAD | 0.387 |
| p95 | 1.491 |
| Method picked | `percentile` |
| Effective threshold | **0.510** |

note:
Numbers from the real `out/bench.jsonl`. The system picks percentile because the tail is not heavy enough to trigger MAD.

---

## 7 · Clustering

- Graph: node = word, edge = distance < threshold
- **Union-find** with path compression
- Order-invariant, deterministic
- Optional **k-NN prefilter**: O(V²) → O(V·K)

note:
Union-find is elegant and classic. The k-NN prefilter is optional but transformative on big V.

---

## 8 · Compression estimate

```
size_compressed ≈ #clusters + 0.5 · #tokens
ratio = size_compressed / size_original
```

<span class="danger">Toy model</span> — not comparable to gzip.

note:
Brutal honesty: it is a thermometer. Real comparison needs entropy coding (Huffman / arithmetic / ANS).

---

## Live demo · sample.txt

```bash
npm run bench -- --file ./samples/sample.txt --auto \
  --autoMethod hybrid --autoStats
```

| Metric | Value |
|--------|-------|
| Unique words | 65 |
| Clusters found | 3 |
| Total time | 13 ms |
| `savingsPct` | **54.5%** |

note:
Live run. Show the JSON line printed by bench. Open the HTML report side by side.

---

## The clusters found (sample.txt)

- <span class="accent">Cluster A</span> (63 words) — representative: "la"
  - articles, prepositions, auxiliaries, common verbs
- <span class="accent">Cluster B</span> (1) — "pensieri"
- <span class="accent">Cluster C</span> (1) — "regolare"

note:
On Kafka's five-line opening (Italian), three families emerge. The two singletons show the system can keep rarities apart.

---

## What it is **not**

- Not a file compressor (no .gz)
- Does not understand sentences, lemmas, morphology
- Does not know the meaning of words
- Does not compare bytes to gzip/brotli/zstd

note:
The most important slide. Without honesty about limits, the 54.5% number is misleading.

---

## Honest limits

- Toy model for compression
- O(V²) on the vocabulary (mitigated by k-NN)
- Sensitive to parameters
- Small corpora → distances collapse
- Only one language tested well (Italian)

note:
Compact slide: the audience sees the boundaries of the prototype at a glance.

---

## Use cases (today)

<div class="columns">
<div>

- 🎓 **Teaching**
  - Union-find
  - Sparse matrices
  - Poincaré disk

</div>
<div>

- 🔬 **Research**
  - Hyperbolic embeddings
  - Auto-thresholding
  - Parameter sweeps

</div>
</div>

- 🧪 **Exploratory NLP**: word families, de-facto stop-words

note:
Three macro areas. Remember: it is a demo, not a product.

---

## Improvement roadmap

| Front | Move |
|-------|------|
| Real compression | Entropy coder (Huffman/arithmetic/ANS) |
| Decompressor | Canonical representatives |
| Scalability | Truncated SVD, approximate k-NN (HNSW) |
| Semantic quality | TF-IDF/PMI, Poincaré GloVe |
| Validation | Multilingual, gold-standard suites |

note:
Each row is its own project. Open issues / discussions on GitHub for contributors.

---

## Why I built it this way

- **Zero required dependencies** → readable & teachable
- **Determinism via seed** → every experiment is reproducible
- **Embedded smoke tests** → trust and verify
- **Full diagnostics** → auto-threshold is not a black box

note:
Design choices serve community-friendly distribution. No deps means it runs anywhere.

---

## Architecture, in 5 files

```
compressionTest.js    ← engine (8 stages)
bench.js              ← benchmark CLI
tools/pretty-report.js ← HTML report
samples/sample.txt    ← Italian demo
out/bench.jsonl       ← results
```

note:
Compactness is a feature, not a bug. The whole prototype fits in a few hundred lines.

---

## Reference numbers (sample.txt)

```json
{ "uniqueWords": 65, "clusters": 3,
  "ratio": 0.4551, "savingsPct": "54.5",
  "clusterThresholdUsed": 0.5097,
  "median": 0.6803, "mad": 0.261, "p95": 1.491 }
```

<span class="muted small">Run with `--auto --autoMethod hybrid --autoStats`</span>

note:
Pure traceability slide. Anyone wanting to reproduce has all numbers in front of them.

---

## Lessons learned

1. Hyperbolic geometry pays off only on hierarchies.
2. Random projection is enough for an MVP.
3. Robust thresholding (MAD) protects from pathological distributions.
4. Diagnostics beat magic numbers.
5. Honest limits beat marketing numbers.

note:
Five take-aways I'd love to see in the audience's notes.

---

## Frequently asked questions

> "Does it really compress?" — *No, it estimates.*
>
> "Compared to gzip?" — *Not yet, see roadmap.*
>
> "Other languages?" — *Technically yes, not validated.*
>
> "Production-ready?" — *No, it's research.*

note:
Pre-empting questions saves Q&A time.

---

## Resources

- Repo · `JacoVame/noeucompression`
- Docs IT · [`docs/it/`](../../docs/it/README.md)
- Docs EN · [`docs/en/`](../../docs/en/README.md)
- Animated pipeline · [`docs/diagram/pipeline.html`](../../docs/diagram/pipeline.html)
- Story · [`docs/en/story.md`](../../docs/en/story.md)

note:
Final link slide. If possible, project a QR pointing to the repo.

---

<!-- .slide: class="title" -->
# Thank you

<div class="author">Gianluca Gagliano</div>
<div class="muted small">Questions, experiments, contributions: open an issue/discussion on GitHub.</div>
<div class="muted small">MIT License · 2026</div>

note:
Leave 5–7 minutes for Q&A. Return to the animated pipeline if visual prompts are needed.
