# CLAUDE.md — phase2 (binding rules for agent sessions)

You are working inside `phase2/` of the `noeucompression` repository, on branch `phase2`.

## The packet discipline
- **One session = one phase.** Read `README-fase2.md`, identify the current phase, deliver its DoD, stop. Do not start the next phase in the same session.
- A phase is done only when its **binary DoD** passes. No "mostly working". If the DoD cannot be met, report the blocker; do not redefine the DoD.

## The wall
- After Phase 1 is merged, **the harness is frozen** — `eval.py` and everything under `harness/`. If your task is implementing embeddings (Phases 2–3) you MUST NOT edit them; create only under `embeddings/` (and later `ablation.py`) and call the harness as a black box. If a metric seems wrong, report it and stop; only the human PM may unfreeze it (dated note in README-fase2.md).
- Never tune hyperparameters against the gold labels of the final test split. Synthetic trees are for iteration; WordNet-mammals is the report set.

## Reproducibility (F3 is always in force)
- Every script accepts `--seed` (default 20260716) and sets `torch.manual_seed` + `numpy` seed from it.
- Every artifact goes to `out/` with the seed in the filename (e.g. `out/map_d2_seed20260716.json`).
- Any result you state in a summary must be regenerable by a single command that you print verbatim.

## Environment
- Windows host. The venv lives **outside the repo tree** (default `%LOCALAPPDATA%\noeu-venvs\phase2`); the interpreter path is recorded in `.venv-path` (git-ignored). Always invoke Python via that path, never a bare `python`.
- Rationale (do not "fix" this): nltk ≥ 3.10 ships a CWD-import security guard (`nltk/inisec.py`, CWE-427 mitigation) that blocks any dependency resolving from a subdirectory of the current working directory. An in-tree venv is a permanent false positive. The out-of-tree venv is the structural solution; never set `NLTK_DISABLE_IMPORT_SECURITY`.
- Keep `PYTHONSAFEPATH=1` in the session environment (`setup.ps1` sets it for its children).
- Never install packages globally; if a new dependency is needed, add it to `requirements.txt`, reinstall, and refresh `requirements.lock.txt`.
- Torch is CPU-only by design; the experiments are small. Do not add CUDA logic.

## Scope guards
- The JS companion in the repo root is **out of scope**: never edit it in phase-2 sessions.
- Optimization lives on the **Lorentz** manifold (`geoopt`); the Poincaré ball appears only in visualization code.
- No new frameworks, no experiment trackers, no config systems: argparse + JSON + matplotlib is the ceiling.

## Honesty
- Report negative results exactly like positive ones. F1 firing is a finding, not an embarrassment to hide.
- Plots must show mean ± σ across seeds, never a cherry-picked seed.
