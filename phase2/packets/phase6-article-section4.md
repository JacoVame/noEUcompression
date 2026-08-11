# Packet — Phase 6: carta 02 "Misurare l'Invisibile"

**The premise was corrected on 2026-08-04.** An earlier version of this packet
assumed carta 02 existed and needed its §4 upgraded. It does not exist: it is to be
**written**, from the Phase-2 programme results, in a separate Claude project (web
side). Only its teaser image is on disk
(`C:\Users\gianluca.g\Downloads\teaser_carta02_misurare_invisibile.png`,
2026-08-03). Carta 01 — *"Mappare l'Invisibile"* — is on disk at
`C:\Users\gianluca.g\Downloads\mappare_invisibile_v2.md` (Italian, ~17k chars,
§1-§4 plus *Sintesi* and *Cosa questo articolo non afferma*).

So this repository's job for Phase 6 is **not to write the article**. It is to
supply everything the writing project needs, and later to verify the draft against
the artifacts.

## What has already been delivered (2026-08-04)

- **[`../report/carta02-dossier.md`](../report/carta02-dossier.md)** — the evidence
  dossier, in Italian, self-contained: the question inherited from §4 of carta 01,
  the measuring apparatus and why it was frozen first, the fairness protocol
  (F1/F2/F3, the regression gate, the per-(geometry, dimension) tuning), the full
  result table, the crowding mechanism with the measured spreads, the depth band,
  ready-to-use figure captions, the list of things the article must NOT claim, a
  claim-to-evidence table, the reproduction command, and a proposed section
  structure. Every number in it traces to an `out/` artifact.
- **`out/carta02-bundle/`** and **`out/carta02-bundle.zip`** (git-ignored like
  everything in `out/`) — the dossier plus the figures plus the aggregate tables,
  assembled for upload into the Claude project. Regenerate the bundle by re-running
  the commands in §10 of the dossier and copying the named artifacts.

**Job 1 was executed on 2026-08-11**, extended past Phase 4b to Phases 5, 5b, 5c
and 5d. The dossier now carries a §4c (the reconnected pipeline and the
reward-hackable ratio), a fourth figure caption for
`report/rate_distortion_wordnet-mammals_d2-5-10_seedset20260716x5.png`, three new
bullets in §7, a rewritten Phase-5 entry in §8, six new rows in §9, the four
Phase-5 regenerate commands in §10, and a restructured §11. The bundle was
re-assembled: 20 files, 464 KB, adding `FINDINGS.md`, the rate–distortion figure,
the `compress_*` aggregates, the mapping and the decode-verification summary. Only
**Job 2** below remains.

## What the writing project needs from a human

Upload `out/carta02-bundle.zip` (or its six files) into the Claude project for
carta 02. The dossier is written to be the single source of truth there: it is
deliberately in Italian, which is the one exception to the English rule for
`phase2/` docs, because it feeds an Italian article.

## What remains for a Phase-6 session in this repository

Two jobs, both verification rather than authorship. Paste the block below when the
draft of carta 02 exists.

```text
Read ./CLAUDE.md, ./README-fase2.md and ./report/carta02-dossier.md. Current phase:
6 (carta 02 "Misurare l'Invisibile").

carta 02 is authored in a separate Claude project, not here. Your job is the two
things that project cannot do for itself, because it has no access to the
artifacts.

Job 1 — keep the dossier true. DONE 2026-08-11 for Phases 4b and 5-5d; re-run only
if a further phase lands. The rule it followed: fold the new result into §7 ("Cosa
carta 02 non deve affermare") and §8 ("Cosa manca ancora") of
report/carta02-dossier.md, give it its own §4x section if it carries numbers, and
re-assemble out/carta02-bundle.zip afterwards. Change nothing else in the dossier
unless a number in it is wrong.

Job 2 — fact-check the draft. Given the draft of carta 02 (the PM will paste it or
give a path), verify every empirical claim against the artifacts, not against the
dossier's prose:
  - out/ablation_table_wordnet-mammals_dims2-5-10_seedset20260716x5.{json,md}
  - out/ablation_run_*.json for per-seed numbers
  - the three out/ablation_*_wordnet-mammals_dims2-5-10_seedset20260716x5.png
If out/ is empty, regenerate it first with the single Phase-4 command (~3.5 h
cold); artifacts are git-ignored by decision.

Report every discrepancy as a table: claim as written, what the artifact says,
severity. Flag in particular, because these are the failure modes that matter:
  - a number that drifted (rounding, a σ dropped, a mean rank quoted as a MAP);
  - the d>=5 reversal being softened or omitted — hyperbolic wins unambiguously
    only at d=2, and from d=5 the Euclidean baseline takes reconstruction outright;
  - the distortion gap described as monotone (it is +0.0831 at d=2, -0.0012 at
    d=5, +0.0320 at d=10);
  - the depth advantage described as growing with depth (it is a band: crossing
    between depth 4 and 5, best at 6, closed again by 9);
  - MAX_SPATIAL_NORM presented as anything other than a numerical guard, or its
    reach understated (721.4/1170 nodes at d=2, ~7% at d=5 and d=10);
  - any claim of compression ratio or gzip comparison: the gzip comparison is a
    declared non-goal, and Phase 5 (dossier §4c, FINDINGS.md) measured the ratio
    and found it anti-correlated with fidelity — so a ratio quoted as compression is
    wrong on the evidence, not merely out of scope. Also flag any Phase-5 number
    quoted without its 1.55% token coverage, and the unit-free prototype ratio that
    reads as ">90% compression";
  - prior art: Ontrup & Ritter (NIPS 2001) and Nickel & Kiela (2017, 2018) must
    stay credited as the origin of the method — what is ours is the measurement.

DoD (binary): a discrepancy report where every empirical claim in the draft is
either confirmed against a named artifact or listed as a discrepancy, plus the
single command that regenerates the evidence. Do not rewrite the article's prose:
if a sentence is unsupported, say what the artifact supports instead and let the
author choose the words.

Do not touch eval.py, harness/, embeddings/, or the sealed parts of ablation.py.
Do not restyle the figures. Do not edit the JS companion.
```

## The one thing the article must keep

§4 of carta 01 argues that hyperbolic space has room for trees because disc area
grows exponentially with radius, and confesses that this repository did not learn
its embeddings. Phase 2-4 closed the confession — the embeddings are learned now —
and *qualified* the argument: the geometry pays where dimension is scarce,
decisively at d=2, and stops paying on reconstruction by d=5. Carta 02 earns its
credibility by reporting the second half.
