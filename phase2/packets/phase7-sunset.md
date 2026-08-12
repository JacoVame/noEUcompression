# Packet — Phase 7: formal sunset

**What this is.** The last phase. `NOT-DONE.md` names what would make this a
*different* project rather than an unfinished one, `v1.0` marks the measurement
programme closed, and Job 2 — the fact-check owed since the original Phase-6
packet — gets folded in here rather than left open indefinitely (PM decision,
2026-08-12).

**Scope decision the PM should confirm or override.** This packet places
`NOT-DONE.md` at `phase2/NOT-DONE.md`, not the repo root, because every item on
its list is specific to the phase-2 geometric-embedding study (Route B, WSD, a
learned SOM, a second taxonomy) — none of it is about the JS companion or the
docs tree. If the PM wants a repo-root sunset note instead (covering the whole
`noeucompression` project, JS prototype included), edit the path below before
pasting.

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md, ./README-fase2.md, ./FINDINGS.md and
./packets/phase7-sunset.md. Current phase: 7 (formal sunset, final phase).

Deliver, and nothing else:

  1. Tag `v1.0` — annotated git tag on HEAD, message: one sentence stating what
     was measured and the headline finding (curvature pays at d=2, the
     downstream ratio rewards degradation — pull the exact wording from
     FINDINGS.md's one-sentence result, don't rephrase it).
  2. Write `phase2/NOT-DONE.md` listing, each with one sentence of why it is
     out of scope for v1.0 rather than a defect:
       - Route B (co-occurrence / PMI signal) — Locked decision #3 confined
         this study to Route A (gold WordNet hierarchy) only.
       - Word-sense disambiguation — the mapping resolves 19 ambiguous types
         by sense number (Phase-5 record), not by a real WSD model.
       - A learned hyperbolic SOM — Ontrup & Ritter (2001) is credited as the
         method's origin but a SOM was never built; this study only trained a
         point embedding on the Lorentz manifold.
       - A second taxonomy — every result in FINDINGS.md is `wordnet-mammals`
         only; nothing here shows the d=2/d>=5 pattern holds outside one
         hierarchy.
  3. Job 2 (folded in, PM decision 2026-08-12): fact-check
     `docs/it/cantiere-fase2.md`, `docs/en/phase2-note.md`, and
     `report/carta02-dossier.md` sentence by sentence against `FINDINGS.md`,
     `README-fase2.md`'s Phase-4/5/5b/5c/5d/5e records, and named `out/`
     artifacts. Report drift, do not silently rewrite: a one-digit transcription
     slip may be fixed inline with a note in the session report; anything that
     changes a claim's meaning is reported to the PM, not corrected unilaterally.

DoD (binary), all three together:
  1. `git tag -l v1.0` shows the tag, annotated (`git cat-file -p v1.0` shows a
     tag object, not a lightweight ref), pointing at the commit this session
     lands on.
  2. `phase2/NOT-DONE.md` exists with exactly the four items above (or the
     PM's edited list, if changed before pasting), each with its one-sentence
     reason.
  3. The fact-check pass is reported in the session summary — either "no drift
     found" or a table of (sentence, stated number, correct number, source) —
     covering all three documents named in step 3.

Rules:
  - No new measurement. This is a writing + git packet, same ceiling as
    Phase 6.
  - `v1.0` is a research sunset tag, not a software release: the message
    should read as "the measurement programme is closed," not "ship this."
  - `NOT-DONE.md` is not a roadmap and makes no promise of a v2. Per CLAUDE.md,
    anything on it stays closed unless a human PM reopens it with a dated note.
  - Scope: `phase2/NOT-DONE.md` (new file), the git tag, and the read-only
    fact-check pass over the three named documents (edits only for confirmed
    drift, reported either way). `eval.py`, `harness/`, `embeddings/`,
    `ablation.py`, `compress.py`, `decode.py` untouched. No new file under
    `docs/` or the repo root beyond what step 3 might correct in the two notes
    or the dossier.
  - After this phase, per CLAUDE.md's packet discipline, there is no Phase 8:
    stop.

Environment: Windows host, interpreter from `.venv-path`, `PYTHONSAFEPATH=1`.
Job 2's fact-check needs no Python — it is a document-vs-document comparison.
```

## Why Job 2 is here and not a separate packet

Job 2 has been open since the original Phase-6 packet (`phase6-article-section4.md`),
carried as a loose thread through the redefinition of Phase 6 into the public
cantiere note. It never got its own phase slot, and leaving it open past the
sunset tag would mean shipping `v1.0` over an unverified published claim. Folding
it into Phase 7 closes it before the tag, not after.

## What is deliberately not on the `NOT-DONE.md` list

Phase 5b's matched-K comparison — the one conditional item the original Phase-7
row in `README-fase2.md` named ("plus Phase 5b's undelivered matched-K comparison
if it is retired rather than run") — is not carried over. Phase 5e delivered it
on 2026-08-11. Re-reading the phase-7 DoD row in `README-fase2.md` before running
this packet is worth doing once, in case anything else there has since been
resolved the same way.
