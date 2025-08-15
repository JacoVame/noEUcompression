# When AI Becomes a Multiplier for Theoretical Research

Today I want to share a case study that shows how Artificial Intelligence, used with intent and care, can radically transform research in theoretical computer science. This is not about simple code generation, but about accelerated scientific inquiry at levels that until recently seemed out of reach.

## Semantic Compression in Hyperbolic Spaces

The work I created over the last two days explores a frontier: compressing text through non‑Euclidean geometries. The underlying idea is not revolutionary and likely has prior art in the literature; without access to every academic publication, I chose to explore the idea I had in mind anyway. Instead of the traditional statistical patterns, I tried using hyperbolic geometry.

The idea is to use the hyperbolic space of the Poincaré disk to capture the deep semantic structure of natural language.

Example:

Sentence: “Maria gave Luca a book yesterday.”
Deep structure: agent = Maria, action = give, object = book, recipient = Luca, time = yesterday. If we write “Yesterday Luca received a book from Maria,” the words change, but the deep semantic structure remains the same.

The goal is to model this structure (relationships and meaning hierarchies) so that words that are “close” in meaning end up close in the hyperbolic space too.

The Poincaré disk is a way to represent a “curved” world entirely inside a circle. Imagine a map enclosed in that circle: the edge is like a boundary you can never actually reach, even as you get arbitrarily close. Near the center there is “more room” and everything looks less compressed; moving toward the edge, space seems to stretch and distances grow. The shortest roads between two points appear as curved arcs, not straight lines. This is useful for showing structures with many levels and branches: you can place the root at the center and fan out the levels, giving plenty of room to the branches; similar elements remain near each other while very different ones end up far apart.

For intellectual honesty: it had been about 25 years since I last approached these ideas. I apologize in advance for any imprecision; I’m not a mathematician, and many implications would require deeper study.

On day one I revisited and reread (not fully studied—that would take months) concepts I thought I had forgotten; on day two I hammered prompts like there was no tomorrow (many were failures at first).

The system (very simple, really) implements a pipeline with several steps:

1. Intelligent preprocessing: Unicode‑aware tokenization with normalization (NFKC) to make equivalent characters consistent.
2. Co‑occurrence analysis: build a sparse matrix of words that appear near each other, with configurable context windows and weights that decay with distance.
3. Geometric projection: random projections ("random"), take the first components ("firstD"), or use singular value decomposition (SVD).
4. Hyperbolic embedding: project into the Poincaré disk to preserve (as much as possible) semantic distances between words.
5. Semantic clustering: union–find over hyperbolic distances, with optional k‑NN pre‑filtering.
6. Adaptive auto‑tuning: automatically choose thresholds via percentiles, median absolute deviation (MAD), or a hybrid method.

What I want to highlight is how I used AI not to replace theoretical reasoning, but to amplify it exponentially.

AI (I won’t say which) allowed me to:

- Rapidly explore multiple projection strategies
- Implement and test complex algorithms in record time
- Create visualizations and a fairly sophisticated benchmarking setup

Thanks to people like Professor Vito Di Gesù and Professor Domenico Tegolo, my university mentors in Computer Vision, I learned about the techniques discussed here. I have just enough background to evaluate their usefulness. That said, results should be compared with existing compressors (e.g., gzip or Brotli) before drawing conclusions. For now, I don’t plan to push this project further—certainly not today.

So, what’s the point?

To keep making the case that AI does not replace human intelligence—it multiplies it. It’s an extraordinarily capable assistant, free of presumption and polemic, that simply needs guidance to produce value.

We are at the dawn of a new era for computer science. AI democratizes access to advanced research, letting individuals compete with entire research teams. But this democratization requires a critical skill: asking the right questions.

The real multiplier is not the technology itself, but the informed way it is used. A theoretical computer scientist who can craft effective prompts and steer AI toward meaningful scientific exploration can see their productivity grow exponentially.

---
**My two cents**: AI is not here to replace us. It’s here to make us 10×, 100× more capable than we used to be.

*In my view, the future belongs to those who can blend human intuition with artificial computational power.*
