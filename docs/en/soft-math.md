# Soft math

← [Index](./README.md)

This page explains *why* the Poincaré disk makes sense, without requiring any background in differential geometry. If you dislike formulas, skip the gray blocks: the thread of the argument is in the prose.

## Different geometries, different distances

In flat (Euclidean) geometry, Pythagoras rules: the distance between two points is the square root of the sum of squared coordinate differences. It is the geometry we learn at school, and it describes a sheet of paper or a football pitch beautifully.

But other geometries exist. On a sphere, two "straight lines" (great circles) always intersect — there are no parallels. On a hyperbolic plane, the opposite happens: from a point off a line pass *infinitely many* parallels. Distances behave accordingly.

## Why a hyperbolic space for language?

Language has a tree structure: "animal" is the parent of "mammal", which is the parent of "dog", "German shepherd", and so on. Each level has more leaves than the previous one, and the tree explodes *exponentially*.

In a flat space of *d* dimensions, the volume available at distance *r* from the centre grows polynomially as *r^d*. To fit a tree with many leaves you quickly need many dimensions.

In a **hyperbolic** space, the volume available grows *exponentially* with the distance from the centre. Near the centre there is little room, but as you move outwards space multiplies. That is exactly the shape of a tree: one root, a few children, many grandchildren.

The Poincaré disk is a *model* of hyperbolic geometry that lives inside a unit circle. It looks finite, but for someone living inside it, the boundary is infinitely far.

## The disk illusion

Picture an Escher engraving: fish that grow smaller as they swim toward the boundary of a circle. From outside they appear to shrink. From inside they are all the same size, because near the boundary the disk's metric grants them as much "ruler" as those at the centre. That is how the Poincaré disk works: our eyes see boundary points as squashed, but the disk metric says each one of them owns the same yardstick.

The price of this illusion is that Euclidean distances (what a ruler measures) and hyperbolic distances (the real ones) diverge dramatically near the boundary.

> ```
> d_H(u, v) = acosh(1 + 2 · ‖u − v‖² / ((1 − ‖u‖²)(1 − ‖v‖²)))
> ```
>
> Translated: take the Euclidean distance squared; divide by how "little hyperbolic room" remains where *u* and *v* sit (the two `1 − ‖·‖²` factors); squash with `acosh`. The result blows up to infinity as *u* or *v* approach the boundary.

## What this means for words

If two words live near the centre, they are about as far apart as we expected (almost-Euclidean). If one drifts to the boundary, suddenly it is far from everything — even though the ruler said they were close.

That is good news for semantics: in our corpus, **functional** words (articles, prepositions, auxiliaries) tend to crowd the centre, while **rare and topical** words drift outward. The hyperbolic metric pulls them apart naturally.

## The practical idea

In short:

1. Build a small fingerprint for each word (a row in the co-occurrence matrix).
2. Project it down to a few dimensions.
3. Squeeze it inside the disk.
4. Compute distances inside the disk.
5. Group words that are close in that metric.

Nothing arcane. What changes versus a classical Euclidean clustering is only the *ruler*.

## For further reading

- *Poincaré Embeddings for Learning Hierarchical Representations* (Nickel & Kiela, 2017) — the motivation for hyperbolic spaces and hierarchies.
- *Hyperbolic Word Embeddings* / *Poincaré GloVe* — trained variants, far from the random projection + scaling approach used here.
- The technical reports in this repo: [`hyperbolic_compression_analysis.md`](./hyperbolic_compression_analysis.md), [`ai_research_showcase.md`](./ai_research_showcase.md).

## Continue

➡️ [Parameters and CLI: every knob](./parameters-and-cli.md)
