# FAQ — Frequently asked questions

← [Index](./README.md)

### Is it a file compressor?

No. It is a **semantic compression estimate**. It does not produce a `.gz` file. For real byte squeezing use `gzip`, `brotli` or `zstd`. See [limitations](./limitations.md) and [improvements](./improvements.md).

### Why "non-EU"?

"Non-EU" = *non-Euclidean*. No regulations, no policies — it is a tongue-in-cheek name meaning "not Euclidean".

### Does it only work in Italian?

Preprocessing is Unicode-aware, so **technically** it works in any letter-based script. All examples and tests, however, are in Italian. On highly inflected languages (Italian itself, German, Finnish) the absence of lemmatisation hurts.

### Do I need to install anything?

No. It runs on **Node.js 16+**, with no required dependencies. `ml-matrix` and `svd-js` are needed only for SVD projection and are optional.

### Can I see it run without writing code?

Yes:
1. `node compressionTest.js` for a textual demo.
2. Open [`docs/diagram/pipeline.html`](../diagram/pipeline.html) in a browser for the animated pipeline.
3. Open [`presentation/en/index.html`](../../presentation/en/index.html) for the slides.

### What is the "Poincaré disk"?

A unit-radius circle in which geometry is hyperbolic, not Euclidean. Near the boundary space dilates to infinity, which makes it perfect for representing tree-shaped structures — like a language's vocabulary. See [soft math](./soft-math.md).

### Why three clusters on `sample.txt`?

Because in a five-line paragraph most words share a similar context (one big cluster), and a few rare words (`pensieri`, `regolare`) end up in singleton clusters. This is exactly what to expect.

### How do I pick `clusterThreshold`?

Short answer: leave `autoThreshold: true`, method `hybrid`. Long answer in [parameters and CLI](./parameters-and-cli.md), section *Quick threshold cheat-sheet*.

### Can I compare results with `gzip`?

Not via `savingsPct`, no — they measure different things. A serious comparison needs the decompressor + a real entropy coder (see [improvements](./improvements.md), section A).

### Are results reproducible?

Yes, given a fixed `seed`. Without a seed the fallback PRNG can yield slightly different vectors.

### Does it work offline?

Yes. All code, all docs, the animated pipeline and the slides run locally without internet (the slides load reveal.js from a CDN, but it can be vendored if needed).

### Can I use it commercially?

The license is MIT, so yes — but bear in mind it is a research prototype: not optimised, not validated for production.

### Who wrote it?

Gianluca Gagliano. Special acknowledgments to Prof. Vito Di Gesù and Prof. Domenico Tegolo, whose work seeded the ideas behind this project.

### Continue

➡️ [The story: what all this means, in prose](./story.md)
