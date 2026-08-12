# NOT-DONE — what `v1.0` deliberately does not cover

This is not a roadmap and it makes no promise of a v2. Per `CLAUDE.md`'s packet
discipline, everything below stays closed unless a human PM reopens it with a
dated note. Each item is out of scope for this measurement programme, not a
defect in it.

- **Route B (co-occurrence / PMI signal).** Locked decision #3 confined this
  study to Route A (gold WordNet hierarchy) only.
- **Word-sense disambiguation.** The mapping resolves 19 ambiguous types by
  sense number (Phase-5 record), not by a real WSD model.
- **A learned hyperbolic SOM.** Ontrup & Ritter (2001) is credited as the
  method's origin, but a SOM was never built; this study only trained a point
  embedding on the Lorentz manifold.
- **A second taxonomy.** Every result in `FINDINGS.md` is `wordnet-mammals`
  only; nothing here shows the d=2/d≥5 pattern holds outside one hierarchy.
