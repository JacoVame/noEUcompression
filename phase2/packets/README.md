# Packets (agent session briefs)

One session = one phase. This folder holds the brief for each phase that has not
been executed yet, written before the session starts so that the scope, the
binary DoD and the gates are fixed by the PM rather than negotiated by the agent
mid-run.

| Packet | Phase | Status |
|---|---|---|
| [phase4b-epoch-sensitivity.md](phase4b-epoch-sensitivity.md) | 4b (addendum) | ready — run this before Phase 6 |
| [phase5-compression-reconnect.md](phase5-compression-reconnect.md) | 5 (optional) | ready, but blocked on two premises stated inside |
| [phase6-article-section4.md](phase6-article-section4.md) | 6 | ready — depends on 4b |

Conventions every packet inherits, so none of them restates it:

- `eval.py` + `harness/` frozen since Phase 1; `embeddings/euclidean.py` sealed
  2026-08-03; `embeddings/lorentz.py` delivered in Phase 3; `ablation.py`
  partially sealed 2026-08-04 (see `../README-fase2.md`).
- The JS companion in the repository root is out of scope for phase-2 sessions.
- F3: `--seed` (default 20260716), every artifact into `out/` with the seed
  identified in the filename, every stated number regenerable by one printed
  command.
- Interpreter from `.venv-path`, `PYTHONSAFEPATH=1`, out-of-tree venv by design.
- stdout is cp1252: printing `σ` raises `UnicodeEncodeError`. Unicode goes in
  UTF-8 files and matplotlib titles only.
