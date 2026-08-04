# Packet — Phase 4b (addendum): epoch-budget sensitivity

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md and ./README-fase2.md. Current phase: 4b (addendum to Phase 4).

Phase 4 shipped the matched ablation with one stated limitation: the epoch budget
was NOT tuned per dimension. It stays at 6000 for both geometries at every d,
because 6000 was the d=2 optimum for both. The article (Phase 6) may go to
technical review, so this packet closes the obvious reviewer question: does the
Phase-4 conclusion depend on that budget?

Deliver that answer and nothing else. Do not touch the Phase-4 conclusion, the
report table, or the figures.

Scope. ablation.py is PARTIALLY SEALED (README-fase2.md, note dated 2026-08-04).
Untouchable: LR_TABLE and _select_lr, the two gates (GATE/regression_gate/
f1_gate), and run_once's seeding-and-scoring path (np.random.seed ->
torch.manual_seed -> datasets.load -> module.build -> harness.metrics.evaluate).
ADDITIVE change is explicitly allowed, and this packet is the additive case: add
an --epoch-scan mode to ablation.py that reuses run_once unchanged, passing a
different `epochs` through the existing _hyperparams injection. eval.py,
harness/, embeddings/euclidean.py and embeddings/lorentz.py stay read-only as
always. The JS companion in the repo root stays out of scope.

The admissibility test is mechanical and you must run it: the regression gate
must still pass, to the digit, on all four cells.

DoD (binary): ONE command produces the epoch-sensitivity table, and one sentence
stating whether 6000 epochs is at or near an interior optimum for BOTH
geometries at d=5 and d=10. Target command:

  python ablation.py --epoch-scan 1500 3000 4500 6000 --dataset synthetic-tree --dims 5 10 --out out/

Rules that carry over unchanged:
  - synthetic-tree ONLY. wordnet-mammals gold labels must not inform any knob.
    This is a tuning-side question and the report set is already spent.
  - learning rates stay at the frozen LR_TABLE values (euclidean 0.5 at every d;
    lorentz 0.005 at d=2, 0.003 at d=5 and d=10). You are scanning one axis, not
    re-tuning two.
  - seeds {20260716, 12345, 777}, the tuning seed set, mean MAP and mean avg
    distortion across them.
  - d=2 is not scanned: its epoch budget was searched in Phases 2 and 3 over
    {1500..6000} and is published. Say so, do not redo it.
  - F3: --seed default 20260716, every artifact into out/ with the seed set
    identified exactly in the filename, any stated number regenerable by one
    printed command.

Report as findings, not footnotes:
  - For each (geometry, d): mean MAP by epoch count. Is 6000 the argmax, a
    plateau, or past the peak? A plateau is the good answer and you should say
    so plainly; "past the peak" for one geometry only is the finding that would
    actually weaken Phase 4, and it must be reported as such.
  - Whether the two geometries want *different* budgets at the same d. That, not
    the absolute optimum, is what F2 is about.

Environment: Windows host, interpreter recorded in .venv-path, always invoked by
that path, PYTHONSAFEPATH=1. WARNING: stdout is cp1252 — printing 'σ' raises
UnicodeEncodeError. ablation.py already funnels printed text through _console();
use it. Unicode belongs in UTF-8 files and matplotlib titles only.

Runtime: 2 geometries x 2 dims x 3 new epoch values x 3 seeds = 36 synthetic
runs, roughly 50-350 s each, so budget 1.5-3 h. The 6000-epoch cells already
exist in out/ as checkpoints and must be reused, not recomputed. Run in the
background and checkpoint as results land; if you must bound anything, log
exactly what was dropped.

Finally: the phase table in README-fase2.md already carries a Phase-4b row marked
"packet ready, not run" — mark it done with the date, and record the result under
the Phase-4 section. If the scan shows the budget
does not bind, say that the stated Phase-4 limitation is now bounded rather than
removed — it is still not a per-dimension tuning.
```
