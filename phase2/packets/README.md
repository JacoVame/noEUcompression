# Packets (agent session briefs)

One session = one phase. This folder holds the brief for each phase that has not
been executed yet, written before the session starts so that the scope, the
binary DoD and the gates are fixed by the PM rather than negotiated by the agent
mid-run.

| Packet | Phase | Status |
|---|---|---|
| [phase4b-epoch-sensitivity.md](phase4b-epoch-sensitivity.md) | 4b (addendum) | done 2026-08-05 — budget bracketed, 6000 on a plateau |
| [phase5-compression-reconnect.md](phase5-compression-reconnect.md) | 5 (optional) | done 2026-08-04 |
| [phase5b-dimensional-sweep.md](phase5b-dimensional-sweep.md) | 5b (addendum) | done 2026-08-05 — see the Phase-5b record in `../README-fase2.md` |
| [phase5c-lossy-decoder.md](phase5c-lossy-decoder.md) | 5c (addendum) | done 2026-08-10 — all 180 cells verified, no discrepancy |
| [phase5d-reframe-and-findings.md](phase5d-reframe-and-findings.md) | 5d (addendum) | done 2026-08-11 — reframe applied, `../FINDINGS.md` written, figure in `../report/` |
| [phase5e-matched-k.md](phase5e-matched-k.md) | 5e (addendum) | done 2026-08-11 — the matched-K clause Phase 5b owed; see the Phase-5e record in `../README-fase2.md` |
| [phase6-article-section4.md](phase6-article-section4.md) | 6 (original) | superseded — carta 02 published 2026-08-05; Job 1 (keep the dossier true) executed 2026-08-11 for 4b and 5-5d; Job 2 (fact-check the text) still open; see the closure plan below |
| [phase6-public-note.md](phase6-public-note.md) | 6 (redefined) | done 2026-08-12 — `docs/it/cantiere-fase2.md` + `docs/en/phase2-note.md` shipped, linked from both docs READMEs and the root README's Measured-results block |
| [phase7-sunset.md](phase7-sunset.md) | 7 (final) | ready — tag `v1.0`, write `phase2/NOT-DONE.md`, and Job 2 (the carta-02 fact-check) folded in per PM decision 2026-08-12 |

Run order for the remaining work: **Phase 7**, the last one. Phases 5b through
6 are done, and with Phase 6 there is no undelivered DoD clause left except
Job 2, which Phase 7 now carries.

## Closure plan (why this project ends)

Phase 6 as originally written — "article §4" — is spent: carta 02 shipped on
2026-08-05. The slot is reused for the public closure, and a Phase 7 exists for
the one thing research repositories never do, which is to stop on purpose.

- **Phase 6 (redefined)** — the public cantiere note on Phase 5 (figure produced
  by 5d), plus a top-level README that routes a visitor in three lines:
  `docs/en/story.md` for carta 01, `phase2/README-fase2.md` for carta 02,
  `FINDINGS.md` for Phase 5. Today a visitor arriving from the published article
  lands on the 2025 JS prototype.
- **Phase 7** — formal sunset: tag `v1.0` and write `phase2/NOT-DONE.md` listing
  what would be a *different project*: Route B over co-occurrence, word-sense
  disambiguation, a learned hyperbolic SOM, a second taxonomy to confirm the
  shape of the boundary. Without a termination criterion a research project is
  not closed, it is abandoned — and abandonment costs a narrative that closure
  does not. Job 2 (the carta-02 fact-check, open since the original Phase-6
  packet) is folded into this phase rather than left open past the tag
  (PM decision, 2026-08-12).

## Conventions every packet inherits, so none of them restates it

- `eval.py` + `harness/` frozen since Phase 1; `embeddings/euclidean.py` sealed
  2026-08-03; `embeddings/lorentz.py` delivered in Phase 3; `ablation.py`
  partially sealed 2026-08-04 (see `../README-fase2.md`). Additive change to a
  sealed module is admissible only if the regression gate still passes to the
  digit on all four cells.
- The JS companion in the repository root is out of scope for phase-2 sessions.
- F3: `--seed` (default 20260716), every artifact into `out/` with the seed
  identified in the filename, every stated number regenerable by one printed
  command.
- Interpreter from `.venv-path`, `PYTHONSAFEPATH=1`, out-of-tree venv by design.
- stdout is cp1252: printing `σ` raises `UnicodeEncodeError`. Unicode goes in
  UTF-8 files and matplotlib titles only.
- `CONSTRAINTS.md` non-goals are binding on prose as well as on code: in
  particular, no comparison against `gzip` or any entropy coder, in any document.
