#!/usr/bin/env python3
"""Phase 5c (addendum): the lossy decoder, and the round-trip gate on Phase 5.

    python decode.py --dataset wordnet-mammals --d 2 --seeds 5 --verify --out out/

Every cost Phase 5 reports is MODELLED: `compress.accounting` computes the code
length and the residual entropy analytically from the cluster assignment, and no
artefact ever travels back from clusters to tokens. This packet builds the
decoder and measures the same quantities from an actual encode -> decode round
trip, then compares them against the numbers *stored in the Phase-5 per-run
records* — never against a re-evaluation of the same formula.

Placement (the choice the packet asks to be stated): a NEW file at the phase2
root, not a block inside compress.py. `compress.py` is imported read-only and
none of its functions change; the untouchable paths (the mapping, the percentile
grid, `accounting`, gold hops) are reused as they are, which is precisely what
makes the comparison a verification rather than a second model.

THE DECODER. For each cluster, a canonical representative: the highest-frequency
mapped type in the cluster, ties broken by lexicographic order, so the choice is
deterministic and seed-independent. Decoding a code stream emits the
representative of each code. No smoothing, no context, no model — it is
`representatives` + `decode` below, and nothing else.

WHAT "RECONSTRUCTED" MEANS (the failure this packet exists to prevent is
re-running the analytic formula and calling it a check):

  * the token stream is re-derived from the corpus body with `compress.tokenize`
    and filtered to the mapped types; its length and type counts must equal the
    mapping's published N and frequencies, or the run stops;
  * the cluster assignment is recomputed from the cached, gated coordinates
    (`compress.coordinates` re-scores every set against its Phase-4 checkpoint)
    and pinned to the stored record: the recomputed auto-threshold and cluster
    count must match the record's, or the cell is reported as drifted;
  * the code length is `ceil(log2 K_used)` where K_used is the number of
    DISTINCT CODES ACTUALLY EMITTED into the encoded stream;
  * the residual is the EMPIRICAL conditional entropy H(type | code), counted
    from the (emitted code, true type) pairs of the round trip itself;
  * the exact-match rate — the fraction of tokens whose decoded type equals the
    original — is counted by comparing the decoded stream to the input stream,
    token by token.

The gate: |modelled - reconstructed| <= 1e-9 bits/token, where modelled is the
record's `bits_per_token_after + residual_bits_per_token` and reconstructed is
the round trip's `ceil(log2 K_used) + H_empirical(type|code)`. The tolerance is
stated as a number because "within rounding error" is not one. Determinism is
asserted, not presumed: every cell's round trip runs twice and the sha256 of the
decoded stream must be byte-identical.

The representative rule is also bounded: a second decode per cell uses a RANDOM
representative from the same cluster (rng seeded per cell from --seed, so the
run stays reproducible), and the exact-match gap between canonical and random
says how much the canonical rule flatters the result.

F3: --seed default 20260716, artifacts land in --out with the seed set in the
filename, and the command above regenerates every number reported. Exit status:
non-zero if any cell fails the gate. Console output is ASCII (cp1252 stdout).

Read-only dependencies: compress.py, ablation.py, harness/, the sealed embedding
modules — reached only through compress's own functions. The JS companion is
invoked by `compress.js_embedding`, never edited. Runtime: minutes (no training;
the coordinates are the cached .npz artifacts, re-gated on load).
"""
import argparse
import hashlib
import json
import math
import os
import sys
from collections import Counter

# PYTHONSAFEPATH=1 is mandatory here (CLAUDE.md): put the script dir back.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402

import ablation  # noqa: E402  (read-only: seed_set, seed_tag)
import compress  # noqa: E402  (read-only: the whole Phase-5 pipeline)
from harness import datasets  # noqa: E402

TOL_BITS = 1e-9  # the stated rounding tolerance, in bits per token


# --------------------------------------------------------------------------- #
# the decoder — this is all of it
# --------------------------------------------------------------------------- #

def representatives(members, freq):
    """cluster id -> canonical representative: highest corpus frequency first,
    lexicographic order breaking ties. Deterministic and seed-independent."""
    return {cid: min(words, key=lambda w: (-freq[w], w))
            for cid, words in members.items()}


def decode(codes, rep):
    """Emit the representative of each code."""
    return [rep[c] for c in codes]


# --------------------------------------------------------------------------- #
# the round trip, measured
# --------------------------------------------------------------------------- #

def round_trip(labels, row_of_type, mapping, stream, cell_rng):
    """Encode the mapped token stream to codes, decode it back, and measure.

    Returns the reconstructed quantities the gate compares: everything here is
    counted from the streams the trip actually produced, not recomputed from
    the analytic formula.
    """
    freq = mapping["freq"]
    cluster_of = {w: int(labels[row_of_type[w]]) for w in mapping["vocabulary"]}
    members = {}
    for word, cid in cluster_of.items():
        members.setdefault(cid, []).append(word)

    codes = [cluster_of[t] for t in stream]           # encode
    rep = representatives(members, freq)
    decoded = decode(codes, rep)                       # decode

    n = len(codes)
    k_used = len(set(codes))
    per_code = Counter(codes)
    joint = Counter(zip(codes, stream))
    residual = -sum((m / n) * math.log2(m / per_code[c])
                    for (c, _), m in joint.items())
    exact = sum(1 for got, want in zip(decoded, stream) if got == want) / n

    # the same trip with a random representative per cluster, to bound how much
    # the canonical rule flatters the exact-match rate
    random_rep = {cid: sorted(words)[int(cell_rng.integers(len(words)))]
                  for cid, words in members.items()}
    exact_random = sum(1 for c, want in zip(codes, stream)
                       if random_rep[c] == want) / n

    return {
        "k_used": k_used,
        "bits_per_token_code": compress._bits(k_used),
        "residual_empirical_bits_per_token": residual,
        "reconstructed_cost_bits_per_token": compress._bits(k_used) + residual,
        "size_after_bits_reconstructed": (
            n * compress._bits(k_used)
            + len(mapping["vocabulary"]) * compress._bits(k_used)),
        "exact_match_rate": exact,
        "exact_match_rate_random_representative": exact_random,
        "decoded_sha256": _digest(decoded),
    }


def _digest(tokens):
    return hashlib.sha256("\x1f".join(tokens).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# the gate: one cell of the stored record vs its round trip
# --------------------------------------------------------------------------- #

def verify_cell(record_cell, trip, threshold):
    """Compare the stored (modelled) cell against the measured round trip."""
    modelled = (record_cell["bits_per_token_after"]
                + record_cell["residual_bits_per_token"])
    reconstructed = trip["reconstructed_cost_bits_per_token"]
    delta = abs(modelled - reconstructed)
    problems = []
    if abs(threshold - record_cell["threshold"]) > 1e-12:
        problems.append(f"threshold drift: recomputed {threshold!r} vs stored "
                        f"{record_cell['threshold']!r}")
    if trip["k_used"] != record_cell["n_clusters"]:
        problems.append(f"cluster-count drift: {trip['k_used']} distinct codes "
                        f"emitted vs {record_cell['n_clusters']} stored")
    if trip["size_after_bits_reconstructed"] != record_cell["size_after_bits"]:
        problems.append(f"size_after drift: {trip['size_after_bits_reconstructed']} "
                        f"bits reconstructed vs {record_cell['size_after_bits']} stored")
    if delta > TOL_BITS:
        problems.append(f"cost mismatch: modelled {modelled!r} vs reconstructed "
                        f"{reconstructed!r} bits/token (|delta| {delta:.3e} > "
                        f"{TOL_BITS:.0e})")
    return {"modelled_cost_bits_per_token": modelled,
            "reconstructed_cost_bits_per_token": reconstructed,
            "delta_bits_per_token": delta,
            "problems": problems}


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main(argv=None):
    args = _parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    if args.dataset != "wordnet-mammals":
        raise SystemExit("Phase 5 ran on wordnet-mammals only; there is nothing "
                         "to verify on another dataset")

    seeds = ablation.seed_set(args.seed, args.seeds)
    tag = ablation.seed_tag(args.seed, args.seeds)
    hierarchy = datasets.load(args.dataset, seed=args.seed)

    print(f"corpus: {compress.CORPUS_TITLE}")
    text, _, body_path = compress.load_corpus(args)
    mapping = compress.build_mapping(hierarchy, text, args)

    # the stream the encoder eats: re-derived, then pinned to the mapping
    stream = [t for t in compress.tokenize(text) if t in mapping["type_to_node"]]
    if len(stream) != mapping["n_tokens_encoded"]:
        raise SystemExit(f"stream drift: {len(stream)} mapped tokens re-derived "
                         f"vs {mapping['n_tokens_encoded']} published; stop")
    if Counter(stream) != Counter(mapping["freq"]):
        raise SystemExit("stream drift: re-derived type frequencies differ from "
                         "the mapping's; stop")
    print(f"  stream: {len(stream)} mapped tokens, frequencies match the mapping")

    results, failures = {}, []
    for side in compress.SIDES:
        if side == "js-cooccurrence" and args.no_js:
            continue
        results[side] = {}
        for seed in seeds:
            record_path = os.path.join(
                args.out, f"compress_run_{side}_{args.dataset}_d{args.d}"
                          f"_seed{seed}.json")
            if not os.path.exists(record_path):
                raise SystemExit(f"missing Phase-5 record {record_path}; the "
                                 f"round trip verifies stored numbers and does "
                                 f"not regenerate them")
            with open(record_path, encoding="utf-8") as fh:
                record = json.load(fh)

            dist, row_of_type = _distances(side, args, hierarchy, mapping,
                                           seed, body_path)
            for pkey in sorted(record["grid"], key=float):
                cell = record["grid"][pkey]
                threshold = compress.auto_threshold(dist, cell["percentile"])
                labels = compress.cluster(dist, threshold)
                rng_a = _cell_rng(args.seed, side, seed, pkey)
                trip = round_trip(labels, row_of_type, mapping, stream, rng_a)
                # determinism gate: the identical trip, from scratch
                rng_b = _cell_rng(args.seed, side, seed, pkey)
                again = round_trip(labels, row_of_type, mapping, stream, rng_b)
                if trip["decoded_sha256"] != again["decoded_sha256"]:
                    raise SystemExit(f"decoder is not deterministic at "
                                     f"{side}/seed{seed}/p={pkey}; stop")

                verdict = verify_cell(cell, trip, threshold)
                results[side].setdefault(pkey, {})[str(seed)] = {**trip, **verdict}
                for problem in verdict["problems"]:
                    failures.append(f"{side} seed={seed} p={pkey}: {problem}")

    aggregate = _aggregate(results, mapping, args, seeds, tag)
    paths = _write_outputs(aggregate, args, tag)
    _report(aggregate, failures, paths, args)
    if failures and args.verify:
        return 1
    return 0


def _distances(side, args, hierarchy, mapping, seed, body_path):
    """The (distance matrix, type -> row) pair for one (side, seed), through
    compress's own functions so the geometry path is the published one."""
    if side in compress.GEOMETRIES:
        coords = compress.coordinates(side, args, hierarchy, seed)
        dist = compress.subset_distances(side, coords, mapping["node_index"])
        row_of = {node: i for i, node in enumerate(mapping["node_index"])}
        row_of_type = {w: row_of[mapping["type_to_node"][w]]
                       for w in mapping["vocabulary"]}
    else:
        vectors = compress.js_embedding(args, mapping, seed, body_path)
        dist = compress.poincare_distances(vectors, mapping)
        row_of_type = {w: i for i, w in enumerate(mapping["vocabulary"])}
    return dist, row_of_type


def _cell_rng(base_seed, side, seed, pkey):
    """One reproducible rng per cell, order-independent."""
    side_id = compress.SIDES.index(side)
    return np.random.default_rng([base_seed, side_id, seed,
                                  int(round(float(pkey) * 10_000))])


# --------------------------------------------------------------------------- #
# aggregate, artifacts, report
# --------------------------------------------------------------------------- #

TRIP_FIELDS = ("modelled_cost_bits_per_token", "reconstructed_cost_bits_per_token",
               "delta_bits_per_token", "exact_match_rate",
               "exact_match_rate_random_representative", "k_used")


def _aggregate(results, mapping, args, seeds, tag):
    sides = {}
    for side, grid in results.items():
        sides[side] = {"grid": {
            pkey: {
                "per_seed": cells,
                **{f: compress._mean_sigma([cells[str(s)][f] for s in seeds])
                   for f in TRIP_FIELDS},
                "max_abs_delta": max(cells[str(s)]["delta_bits_per_token"]
                                     for s in seeds),
            } for pkey, cells in grid.items()}}
        sides[side]["max_abs_delta_over_grid"] = max(
            cell["max_abs_delta"] for cell in sides[side]["grid"].values())
    return {
        "dataset": args.dataset, "dim": args.d, "seeds": seeds, "seed_tag": tag,
        "tolerance_bits_per_token": TOL_BITS,
        "decoder": ("canonical representative = highest-frequency mapped type "
                    "in the cluster, ties broken lexicographically; decoding "
                    "emits the representative of each code"),
        "reconstructed_cost": ("ceil(log2 K_used) + empirical H(type|code), "
                               "K_used = distinct codes emitted, H counted from "
                               "the (code, type) pairs of the round trip"),
        "n_tokens_encoded": mapping["n_tokens_encoded"],
        "operating_points": [p for p in (compress.PERCENTILE,
                                         compress.PERCENTILE_SPARSE)],
        "sides": sides,
    }


def _write_outputs(aggregate, args, tag):
    base = f"decode_verify_{args.dataset}_d{args.d}_{tag}"
    paths = {"json": os.path.join(args.out, base + ".json"),
             "md": os.path.join(args.out, base + ".md")}
    compress._write_json(paths["json"], aggregate)
    with open(paths["md"], "w", encoding="utf-8") as fh:
        fh.write(_markdown(aggregate, args, tag))
    return paths


def _markdown(aggregate, args, tag):
    out = [
        "# Phase 5c — the lossy decoder and its round-trip gate\n",
        f"`{aggregate['dataset']}`, d={aggregate['dim']}, seeds "
        f"{aggregate['seeds']} (`{tag}`), mean ± σ over the seed set. "
        f"Decoder: {aggregate['decoder']}. Reconstructed cost: "
        f"{aggregate['reconstructed_cost']}. Gate tolerance: "
        f"{aggregate['tolerance_bits_per_token']:.0e} bits/token.\n",
    ]
    for p in aggregate["operating_points"]:
        pkey = compress._pkey(p)
        out.append(f"\n## Auto-threshold percentile p = {p}\n")
        out.append("| side | modelled cost (bits/token) | reconstructed cost "
                   "(bits/token) | max \\|delta\\| | exact-match rate | "
                   "exact-match, random representative |")
        out.append("|---|---|---|---|---|---|")
        for side, entry in aggregate["sides"].items():
            cell = entry["grid"].get(pkey)
            if cell is None:
                continue
            out.append(
                f"| {side} | {compress._pm(cell['modelled_cost_bits_per_token'], 6)} | "
                f"{compress._pm(cell['reconstructed_cost_bits_per_token'], 6)} | "
                f"{cell['max_abs_delta']:.3e} | "
                f"{compress._pm(cell['exact_match_rate'], 4)} | "
                f"{compress._pm(cell['exact_match_rate_random_representative'], 4)} |")
    out.append("\n## The whole grid\n")
    out.append("| side | cells (percentile × seed) | max \\|delta\\| over the "
               "grid (bits/token) |")
    out.append("|---|---|---|")
    for side, entry in aggregate["sides"].items():
        n_cells = sum(len(cell["per_seed"]) for cell in entry["grid"].values())
        out.append(f"| {side} | {n_cells} | "
                   f"{entry['max_abs_delta_over_grid']:.3e} |")
    out.append("")
    return "\n".join(out)


def _report(aggregate, failures, paths, args):
    """Console output is ASCII: this stdout is cp1252 and 'σ' raises there."""
    print()
    print(f"=== Phase 5c - round-trip verification, {aggregate['dataset']} "
          f"d={aggregate['dim']}, {aggregate['seed_tag']} ===")
    print(f"tolerance: {aggregate['tolerance_bits_per_token']:.0e} bits/token "
          f"on |modelled - reconstructed|")
    for p in aggregate["operating_points"]:
        pkey = compress._pkey(p)
        print()
        print(f"-- p = {p}")
        head = (f"{'side':<16}{'modelled b/tok':>18}{'reconstructed':>18}"
                f"{'max |delta|':>14}{'exact match':>20}{'random rep':>20}")
        print(head)
        print("-" * len(head))
        for side, entry in aggregate["sides"].items():
            cell = entry["grid"].get(pkey)
            if cell is None:
                continue
            print(f"{side:<16}"
                  f"{cell['modelled_cost_bits_per_token']['mean']:>18.6f}"
                  f"{cell['reconstructed_cost_bits_per_token']['mean']:>18.6f}"
                  f"{cell['max_abs_delta']:>14.3e}"
                  f"{compress._ascii(cell['exact_match_rate'], 4):>20}"
                  f"{compress._ascii(cell['exact_match_rate_random_representative'], 4):>20}")
    print()
    for side, entry in aggregate["sides"].items():
        n_cells = sum(len(cell["per_seed"]) for cell in entry["grid"].values())
        print(f"  {side:<16}{n_cells} cells verified, max |delta| over the grid "
              f"{entry['max_abs_delta_over_grid']:.3e} bits/token")
    print()
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for line in failures:
            print(f"  {line}")
    else:
        print("all cells PASS: the Phase-5 cost accounting is verified by the "
              "round trip")
    print()
    for name, path in paths.items():
        print(f"  {name}: {path}")
    print()
    print("regenerate:")
    print(f"  python decode.py --dataset {args.dataset} --d {args.d} "
          f"--seeds {args.seeds} --verify --out {args.out}")


def _parse_args(argv):
    p = argparse.ArgumentParser(
        description="Phase 5c: encode->decode round trip over the Phase-5 "
                    "clusterings; verifies the stored cost accounting.")
    p.add_argument("--dataset", default="wordnet-mammals", choices=datasets.DATASETS)
    p.add_argument("--d", "--dim", dest="d", type=int, default=2,
                   help="embedding dimension of the Phase-5 records to verify")
    p.add_argument("--seeds", type=int, default=5,
                   help="how many seeds: base, base+1, ..., base+seeds-1")
    p.add_argument("--seed", type=int, default=compress.DEFAULT_SEED,
                   help="base seed of the seed set")
    p.add_argument("--out", default="out")
    p.add_argument("--verify", action="store_true",
                   help="exit non-zero if any cell fails the gate (the "
                        "comparison itself always runs)")
    p.add_argument("--max-vocab", type=int, default=0,
                   help="must match the Phase-5 run being verified (0 = no cap, "
                        "the published setting)")
    p.add_argument("--corpus-file", default=None,
                   help="use this text instead of fetching PG #2300 (offline)")
    p.add_argument("--no-js", action="store_true",
                   help="skip the js-cooccurrence side (needs node on PATH)")
    args = p.parse_args(argv)
    args.dim = args.d  # compress.coordinates / js_embedding read args.dim
    return args


if __name__ == "__main__":
    sys.exit(main())
