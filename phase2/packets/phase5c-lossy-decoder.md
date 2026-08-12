# Packet — Phase 5c (addendum): the lossy decoder and its gate

Paste the block below as the opening message of a fresh session.

```text
Read ./CLAUDE.md and ./README-fase2.md. Current phase: 5c (addendum to Phase 5).

Every number Phase 5 reports about cost is currently MODELLED: the code length and
the residual entropy are computed analytically from the cluster assignment, and no
artefact ever travels back from clusters to tokens. Until a decoder exists, those
numbers are declared. After it exists, they are verified. That is the whole point
of this packet, and it is the difference between the thermometer of carta 01 and a
measurement.

Deliver the decoder and its round-trip gate, and nothing else. Do not change any
reported number; if a number turns out to be wrong, report the discrepancy and
stop — do not silently correct it.

Scope. New file embeddings/../decode.py at the phase2 root, or an additive block
inside compress.py; your choice, stated in the report. ADDITIVE only. Untouchable:
the mapping path, the percentile grid, the accounting functions, gold_hops.
eval.py, harness/, embeddings/euclidean.py, embeddings/lorentz.py and ablation.py
stay read-only. The JS companion in the repo root stays out of scope.

What the decoder is. Twenty lines, not two hundred. For each cluster, a canonical
representative — the highest-frequency mapped type in that cluster, ties broken by
lexicographic order so the choice is deterministic and seed-independent. Decoding a
code stream means emitting the representative of each code. That is all it does:
no smoothing, no context, no model.

DoD (binary): at EVERY operating point of the existing grid, on EVERY side, the
cost reconstructed from an actual encode->decode round trip equals
bits_per_token_after + residual_bits_per_token to within rounding error. ONE
command produces the comparison table and exits non-zero if any point fails.
Target command:

  python decode.py --dataset wordnet-mammals --d 2 --seeds 5 --verify --out out/

Rules:
  - "Reconstructed cost" is measured, not recomputed from the same formula. Encode
    the token stream to codes, decode it back to types, and derive: the code length
    from the actual number of distinct codes used, and the residual from the
    EMPIRICAL conditional entropy of the true type given the emitted code. If your
    residual is the analytic H(type|cluster) again, you have verified nothing —
    that is the failure this packet exists to prevent.
  - Report the exact-match rate: the fraction of tokens whose decoded type equals
    the original. This is the loss made concrete, and it belongs next to every
    ratio the repo prints.
  - Rounding tolerance must be stated as a number in the report, not left implicit,
    and it must be tight: 1e-9 on bits per token unless you can justify looser.
  - The decoder must be deterministic: two runs with the same seed produce
    byte-identical output. Assert it in the gate.
  - F3: --seed default 20260716, artifacts into out/ with the seed set identified
    in the filename, every stated number regenerable by one printed command.

Report as findings, not footnotes:
  - The comparison table: per side and per operating point, modelled cost versus
    reconstructed cost, and the delta.
  - The exact-match rate per side and per operating point.
  - Any point where modelled and reconstructed disagree beyond tolerance, with the
    cluster and the types involved. A disagreement is a finding about Phase 5, not
    a bug in this packet, and it must be reported as such rather than absorbed.
  - Whether the canonical-representative choice changes the exact-match rate
    materially versus a random representative from the same cluster. One extra run
    answers it and it bounds how much the representative rule flatters the result.

Environment: Windows host, interpreter recorded in .venv-path, always invoked by
that path, PYTHONSAFEPATH=1. stdout is cp1252 — funnel printed text through the
existing console helper; Unicode belongs in UTF-8 files and matplotlib titles only.

Runtime: minutes. There is no training and no embedding work in this packet.

Finally: add a Phase-5c row to the phase table in README-fase2.md marked done with
the date, and state in one sentence whether the Phase-5 cost accounting is now
verified or whether the round trip found a discrepancy.
```

## Why this packet matters

It converts the entire Phase-5 cost story from *asserted* to *checked*, at the cost of one short session. It also produces the one number a reader will actually feel — the exact-match rate — which no ratio conveys.
