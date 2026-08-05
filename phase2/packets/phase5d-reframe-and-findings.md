# Packet — Phase 5d (addendum): reframe, and the finding written down

Depends on Phase 5b and Phase 5c. Run last of the three.

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md, ./README-fase2.md and ./CONSTRAINTS.md. Current phase: 5d
(addendum to Phase 5).

Two gestures, one document. Phase 5 established something more interesting than
any compression ratio, and the repository does not currently say it anywhere.

GESTURE ONE — the reframe. Stop calling this compression in the repository prose.
It is semantic quantization, and its honest evaluation plane is rate-distortion:
bits per token against semantic damage. Rename in prose, in section headings, in
the phase table and in the README; do NOT rename artefact filenames in out/, and
do NOT rewrite any historical result — F3 reproducibility depends on those exact
names, and renaming them would invalidate every printed command in the repo. Where
a filename says "compress", leave the filename and explain it once.

GESTURE TWO — FINDINGS.md at the phase2 root. The result to record: the
compression ratio is a metric that rewards degradation. At d=2 across 36
(side, threshold) cells the ratio correlates -0.88 with gold_hops_token_weighted
and -0.92 with the largest-cluster token share; the best ratio of the three sides
belongs to the unlearned heuristic, the most degenerate embedding, whose pairwise
distances are 84.9% exactly zero; and the Lorentz side's own best ratio puts 87% of
tokens in a single cluster with merges spanning 7.49 hops against a
hierarchy-blind reference of 7.65. Nobody was gaming the metric. It happened
because the metric was gameable.

HOW TO FRAME IT — read this twice. CONSTRAINTS.md forbids comparison against gzip
or any entropy coder, and that non-goal is binding on this document too. So the
finding is stated as INTERNAL ACCOUNTING and needs no rival codec: every
configuration in the grid falls on the same iso-cost diagonal, code length plus
residual loss approximately 8 bits per token, meaning bits are MOVED from the code
into the loss roughly one for one rather than saved. The 5.696 bits/token type
entropy stays in the document as a REFERENCE FLOOR that measures how loose the
stated fixed-width code is (9 bits where the types hold 5.696, the same 3.3 bits of
slack on every side, so any ratio measured against it is partly measuring that
slack). It is not a competitor and must not be written as one. A sentence of the
form "the pipeline is worse than X" is out of scope; a sentence of the form "the
declared baseline has N bits of slack, so the ratio partly measures the baseline"
is in scope. This distinction is not pedantry: the first sentence violates a
declared non-goal, the second is the actual result.

Deliver the reframe and FINDINGS.md, and nothing else. No new experiment, no new
number that is not already in out/.

Scope. Prose and documents only, plus one figure. Untouchable: everything under
out/, every accounting function, every result. eval.py, harness/, embeddings/,
ablation.py, compress.py and decode.py are read-only in this packet. The JS
companion in the repo root stays out of scope.

DoD (binary): FINDINGS.md exists and states, with the numbers and their cell
counts, (a) the anti-correlation result including whatever Phase 5b found at d=5
and d=10, (b) the iso-cost diagonal observation, (c) the reference-floor framing
with the explicit note that no entropy-coder comparison is being made and why,
(d) the exact-match rate from Phase 5c, (e) the 1.55% token coverage stated before
any ratio appears in the document. Plus ONE command regenerates the
rate-distortion figure into report/ from the existing aggregates:

  python compress.py --figure rate-distortion --out report/

Rules:
  - The figure is two panels from data already in out/: code length against
    residual loss with the iso-cost diagonals and the zero-loss reference points;
    and code length against gold hops with the hierarchy-blind reference line.
    Nothing in it may be a number this repo has not already measured.
  - ratio_prototype_units must not appear in FINDINGS.md in any form. It reads as
    "96% compression" and it is the one dishonest number available; say once, in a
    footnote, that it exists and why it is not used.
  - Coverage first. 4616 mapped tokens out of 297697 is 1.55%: state it before the
    first ratio in the document, not after.
  - Every claim in FINDINGS.md carries the artefact filename it comes from.

Report as findings, not footnotes:
  - Whether Phase 5b's higher-dimensional cells strengthen, weaken or reverse the
    anti-correlation. If they weaken it, say so — the finding is about d=2 unless
    the data says otherwise.
  - One concrete example of what a good ratio costs semantically, taken from the
    existing cluster dumps rather than invented.

Environment: Windows host, interpreter recorded in .venv-path, PYTHONSAFEPATH=1.
stdout is cp1252; Unicode belongs in UTF-8 files and matplotlib titles only.

Runtime: minutes. This is a writing packet with one plot.

Finally: add a Phase-5d row to the phase table in README-fase2.md marked done with
the date, and link FINDINGS.md from the repository root README so a visitor who
arrives from the published article finds the result rather than the 2025 JS
prototype.
```

## Why this packet matters

The reward-hackable-metric result is the most transferable thing this research produced, and right now it exists only in a chat log and in the PM's head. Written down with its numbers and its framing constraints, it becomes citable — including by the PM's own later work on compartmented validation, where it is the measured instance of a thesis that is otherwise argued from first principles.

## Note on the framing correction

The internal-accounting framing above is a correction to an earlier analysis that stated the result as "the pipeline is worse than entropy coding". The arithmetic was right and the framing was not: it treated an entropy coder as a rival, which `CONSTRAINTS.md` rules out as a non-goal. The iso-cost diagonal says the same thing without a rival, and is inattackable because it is internal to the accounting. Recording the correction here, rather than quietly using the better version, is the point.
