#!/usr/bin/env python3
"""Phase 5 (optional): the compression pipeline, run on the *learned* embeddings.

    python compress.py --dataset wordnet-mammals --dim 2 --seeds 5 --out out/

This file is the whole phase. It resolves the two premises the packet states,
then measures one thing: what the JS prototype's own semantic-compression
accounting does when the co-occurrence embedding at its heart is replaced by the
Phase-3/Phase-4 learned embeddings, Euclidean and Lorentz, at the same
dimension and over the same seed set.

-------------------------------------------------------------------------------
PREMISE 1 — where the end-to-end run lives: Python side, and the DoD is met
-------------------------------------------------------------------------------
`bench.js` builds its embedding internally (`--file/--dimension/--projection`)
and exposes no import path for external coordinates, and the JS companion is
read-only for phase-2 packets. So this module *ports* the prototype's steps 5-8
(distance -> threshold -> union-find clustering -> size accounting) and feeds
them the learned coordinates. `../compressionTest.js` and `../docs/en/pipeline.md`
are the algorithmic reference; nothing in the repo root is edited or imported.

What is ported, line for line, and where it deviates on purpose:

  * step 1, tokenisation: NFKC, lowercase, maximal runs of Unicode letters of
    length >= 2 (`compressionTest.js:90-95`; Python's `str.isalpha` is true for
    exactly the categories `\\p{L}` matches). Cross-checked at run time against
    the JS itself, which must report the same token count or this script fails.
  * step 5, distance: each geometry's *own* metric, taken from the sealed
    embedding module (`embeddings.euclidean._pairwise`,
    `embeddings.lorentz._pairwise`), never re-derived here. The JS baseline keeps
    the Poincaré distance of `compressionTest.js:294-313`.
  * step 6, threshold: the prototype's auto-threshold, `percentile` method. The
    fixed `clusterThreshold: 0.4` is *not* portable: 0.4 means one thing on a
    unit-disk heuristic embedding and nothing at all on a Lorentz embedding whose
    spatial norms reach 1e4. A percentile of the embedding's own distance
    distribution is scale-free, which is precisely why the prototype has it.
    Deviation: the percentile is computed over *all* pairs, exactly, where the JS
    samples 3000 (`autoThresholdSample`); our clustered sets are small enough
    that the exact value costs nothing and removes an RNG.
    Two operating points are reported, and the second is not a knob but a
    consequence of the first: thresholding at the p-th percentile *is* setting
    the edge density of the clustering graph to p, so at the prototype's default
    p=0.35 a 166-node graph sits an order of magnitude above its connectivity
    threshold ln(n)/n = 0.031 and can return nothing but one giant component —
    unless something else intervenes. On the learned embeddings something else
    does, and it is worth stating because it was not predicted: the prototype
    bounds its own auto-threshold to [1e-6, 10] (`compressionTest.js:531-535`),
    and on an embedding whose radius is O(10^3) the 35th percentile is far above
    10, so the *clamp* decides the clustering and the percentile never takes
    effect. The clamp is a scale assumption — the same non-portability the
    percentile rule was introduced to avoid, re-entering through the ceiling
    instead of the floor — so p=0.35 rows are flagged `(clamp)` and read as a
    property of each geometry's radius, not of its shape. `PERCENTILE_SPARSE =
    0.01`, fixed from n alone before any run and below ln(n)/n for both node
    sets, is the point where the percentile rule is actually in force. The full
    grid from p=0.002 to p=0.5 is in the figure and in the JSON.
  * step 7, clustering: union-find over pairs with `d < threshold`, full
    pairwise, `clusterK = 0` (the JS default). Representative = first index.
  * step 8, accounting: *not* ported. See THE CODE below. The prototype's
    estimate is unit-free (`clusters + 0.5 * members`), and the packet forbids
    an unstated code. The prototype's number is still reported alongside, under
    its own name, for continuity.

-------------------------------------------------------------------------------
PREMISE 2 — the signal gap: the corpus, and the size of the intersection
-------------------------------------------------------------------------------
Corpus: Darwin, *The Descent of Man* (Project Gutenberg #2300), English prose,
297_697 tokens. Defence, in one paragraph. The measurement needs an English
text whose vocabulary actually names mammals, because the embedded hierarchy is
`mammal.n.01`'s hyponym closure; `samples/sample.txt` is 511 bytes of Italian
and cannot map at all. Among the candidates examined (`nltk`'s eighteen
Gutenberg texts singly and concatenated, Darwin's *Origin of Species* and
*Voyage of the Beagle*, Wallace's *Malay Archipelago*, Seton's *Wild Animals I
Have Known*, Darwin's *Variation of Animals and Plants under Domestication*),
*The Descent of Man* has the largest intersection with the subtree, and it has
it for a reason rather than by luck: its subject *is* the mammal clade, so its
mammal vocabulary is used in mammal senses — 55.1% of the mapped token
occurrences have their dominant WordNet noun sense inside the subtree, against
14.4% for *Moby Dick*, where "man" and "world" dominate the intersection. The
selection was made on intersection size, which is a precondition of the
measurement and not one of its results; it is disclosed here because it is a
choice, and no metric of the report set informed it. The intersection itself is
reported by every run and is the honest limit of this phase: 259 vocabulary
types map to 166 of the 1170 subtree synsets (14.2% of the hierarchy) and cover
4616 of 297_697 token occurrences (1.55%); everything else is dropped as
unmapped. That is not a handful — 166 clustered nodes, 4616 encoded tokens — but
it is 1.55% of one book, and no sentence below says otherwise.

The mapping, stated so it can be argued with:

  * lemma -> synset. A token matches a subtree synset when the token, or
    `wn.morphy(token, NOUN)` (WordNet's own morphological processor: "dogs" ->
    "dog"), equals one of that synset's single-word lemma names, lowercased.
    Multi-word lemmas (1465 of them, "wild_dog") can never match a token the
    prototype's tokeniser produces, and are counted as unmatchable.
  * ambiguity is resolved, not hidden: when a token's lemma belongs to several
    subtree synsets, the synset in which that lemma has the lowest WordNet sense
    number wins (WordNet orders senses by frequency), tie-broken by the
    hierarchy's BFS index so the choice is deterministic. The count of ambiguous
    types is reported.
  * no word-sense disambiguation is attempted. A token whose corpus sense is not
    a mammal ("bear" the verb, "seal" the stamp) is still mapped if some subtree
    synset carries the lemma. The measured size of that noise is the
    dominant-sense statistic above: ~45% of mapped tokens are being read against
    their most frequent sense. It inflates the token count and adds semantically
    unrelated members to clusters; it cannot flatter one geometry over another,
    since all sides see the identical token stream and node set.

-------------------------------------------------------------------------------
THE CODE the bits are counted under (an unstated code makes a ratio meaningless)
-------------------------------------------------------------------------------
Alphabet: the mapped token stream only. N = mapped token occurrences,
V = distinct mapped types, K = clusters found. Unmapped tokens are outside both
sides of the accounting and are reported separately.

  size_before = N * ceil(log2 V)      bits   -- every token a fixed-width index
                                               into the mapped vocabulary
  size_after  = N * ceil(log2 K)             -- every token a fixed-width
              + V * ceil(log2 K)      bits     cluster id, plus the type ->
                                               cluster table, one id per type in
                                               the vocabulary's canonical order
  ratio       = size_after / size_before

Fixed-width, no entropy coder, no probability model — deliberately, because the
README's non-goals forbid a gzip comparison and any entropy-coded number would
be exactly that comparison in disguise. The spelling dictionary (type -> string)
is not counted: it is identical on both sides. `ratio_ideal` repeats the
arithmetic with fractional log2 (no ceil), since at V=259 the ceil quantises to
9 bits and one cluster more or less can be invisible. `ratio_prototype_units` is
`(K + 0.5 * V) / N`, the prototype's own thermometer
(`compressionTest.js:661-676`), reported for continuity and *not* comparable to
`ratio` — it divides a vocabulary-sized quantity by a token count.

The code is lossy by construction: the decoder recovers a cluster id, hence the
cluster's representative synset, never the token's own type when its cluster
holds more than one. What that destroys is measured, not asserted:
`collapsed_token_fraction`, `residual_bits_per_token` = H(type | cluster) under
the corpus's own type frequencies, `gold_hops_token_weighted` / `gold_hops_max`
= how far apart in the *gold* hierarchy the synsets a cluster merges actually
are (hops, against a subtree diameter of 16), and `largest_cluster_token_share`.

A floor worth separating from the geometry: 259 types map onto 166 synsets, so
`ratio_at_no_clustering` (K = 166, threshold 0, no geometry involved) is the part
of any ratio bought by the lemma -> synset mapping alone.

-------------------------------------------------------------------------------
Scope, seals, reproducibility
-------------------------------------------------------------------------------
Read-only dependencies: `eval.py` and `harness/` (frozen since Phase 1),
`embeddings/euclidean.py` (sealed 2026-08-03), `embeddings/lorentz.py`
(Phase 3), `ablation.py` (partially sealed 2026-08-04) — from which this module
*reuses* `LR_TABLE` (through `_learning_rate`), `EPOCHS`, the `_hyperparams`
injection, `seed_set`/`seed_tag` and `GATE_TOL` rather than restating any of
them. The JS companion is read-only and is invoked, never imported or edited:
`node -e` with an inline script that calls its documented public methods
(`docs/en/parameters-and-cli.md`, "Constructor (programmatic use)").

Coordinates: the Phase-4 checkpoints store metrics only, so this phase re-trains
d=2 for both geometries over the seed set (~64 min on the 22-core host at the
recorded per-run costs) and *persists the coordinates* as its own artifacts,
`out/compress_coords_*.npz`, which makes every later rerun free. Each re-trained
run is gated against its Phase-4 checkpoint: MAP, mean rank and average
distortion must reproduce to `ablation.GATE_TOL`, or this script stops. That
gate is the proof that the coordinates being compressed are the coordinates the
published table describes.

F3: `--seed` defaults to 20260716, aggregates are tagged `seedset<base>x<k>`
(exactly `base .. base+k-1`, seed list written into the JSON), every artifact
lands in `--out`, and the command above regenerates every number reported.

-------------------------------------------------------------------------------
PHASE 5b (addendum) -- the dimensional sweep, `--dims`, additive
-------------------------------------------------------------------------------
    python compress.py --dataset wordnet-mammals --dims 5 10 --seeds 5 --out out/

`--dims` is a second entry point (`main_multi_dim`) alongside the untouched
`--dim` path above; nothing in THE CODE, the percentile grid, the lemma->synset
mapping, or `gold_hops_token_weighted` changes for it -- every function from
`build_mapping` to `accounting` is reused unmodified, at each requested
dimension in turn (a per-dimension `argparse.Namespace` copy supplies `.dim` to
the same `coordinates`/`measure`/`summarise`/`write_outputs`/`report` calls the
`--dim` path already makes). Three rules this mode enforces mechanically:

  * No retraining a Phase-4 checkpoint into existence. Before touching the
    corpus, `_missing_checkpoints` requires every
    `ablation_run_<geometry>_<dataset>_d<dim>_seed<seed>.json` the requested
    dims and seeds need; any gap stops the run and names the missing file
    rather than falling back to a fresh hyperparameter search. Coordinates are
    still *re-derived* per (geometry, dim, seed) -- exactly what the `--dim`
    path already does via `coordinates`/`gate` -- because the checkpoint is a
    metrics record, not a coordinate array; re-deriving from the frozen
    `LR_TABLE` recipe and gating the result to `ablation.GATE_TOL` is what
    "reusing the checkpoint" means here, not a new search.
  * The lemma->synset mapping is computed once and shared across every
    requested dimension (it never reads `args.dim`), which makes "the same
    259 types / 166 synsets at every d" true by construction; on top of that,
    `_check_mapping_invariant` asserts the mapped-type/node counts against the
    published Phase-5 values and stops if they drift, since a silent rebuild
    of the mapping is exactly the defect this packet calls out.
  * The js-cooccurrence side is *not* re-run per dimension. `_load_js_reference`
    loads the five existing `compress_run_js-cooccurrence_..._d2_seed*.json`
    records from Phase 5 and folds them into each dimension's aggregate
    unchanged (`aggregate["js_cooccurrence_source_dim"] = 2`), because it is an
    unlearned heuristic the packet designates a constant reference row rather
    than a per-dimension measurement.

What's new in the output: `phase4_reference` re-derives the Phase-4
euclidean/lorentz MAP and avg-distortion ranking directly from the same
checkpoint files (never transcribed), `rank_by_gold_hops` ranks the sides by
`gold_hops_token_weighted` at each operating point, and `_ranking_verdict`
states, per dimension, whether the gold-hops order matches the MAP ranking,
the distortion ranking, both, or neither -- "neither" is reported as plainly as
a match. `ratio_fidelity_correlation` repeats the d=2 anti-correlation
computation (ratio vs. gold hops, ratio vs. largest-cluster token share, over
`len(SIDES) * len(percentile_grid)` cells) at each new dimension, so it can be
compared to the d=2 figures rather than asserted against them. All of it lands
in one additional pair of artifacts, `compress_dims_<dataset>_dims<d1>-<d2>_
<tag>.{json,md}`, alongside the per-dimension `compress_<dataset>_d<dim>_<tag>`
artifacts the `--dim` path already writes -- nothing is overwritten in place of
what Phase 5 produced at d=2.

-------------------------------------------------------------------------------
PHASE 5d (addendum) -- the rate-distortion figure, `--figure`, additive
-------------------------------------------------------------------------------
    python compress.py --figure rate-distortion --out report/

A third entry point (`main_figure`) that measures nothing. It reads the
aggregates Phase 5 and Phase 5b already wrote into `--aggregate-dir` (default
`out/`) and draws the plane those results live on: code length against the loss
the code buys. No training, no clustering, no accounting call, no artifact in
`out/` touched or rewritten; the only file written is the PNG, into `--out`.

The one quantity re-derived rather than read is the hierarchy-blind gold-hops
reference -- the all-pairs mean shortest path over the 166 clustered synsets in
the frozen hierarchy, 7.654 -- which comes from `harness.datasets` and the
published mapping, and from no embedding. Everything else on both panels is a
number already in the aggregates.
"""
import argparse
import hashlib
import importlib
import json
import math
import os
import subprocess
import sys
import time
import unicodedata
import urllib.request
from collections import Counter
from itertools import groupby

# PYTHONSAFEPATH=1 is mandatory here (CLAUDE.md), so the script directory is not
# on sys.path. Same fix as eval.py and ablation.py: put it back, from __file__.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

matplotlib.use("Agg")  # headless build host
import matplotlib.pyplot as plt  # noqa: E402

import ablation  # noqa: E402  (read-only: LR_TABLE, EPOCHS, _hyperparams, tags)
from harness import datasets, metrics  # noqa: E402

# --- the corpus, pinned (Premise 2) ------------------------------------------
CORPUS_ID = 2300
CORPUS_TITLE = "Darwin, The Descent of Man (Project Gutenberg #2300)"
CORPUS_URL = f"https://www.gutenberg.org/cache/epub/{CORPUS_ID}/pg{CORPUS_ID}.txt"
# sha256 of the raw bytes as fetched 2026-08-04. Project Gutenberg regenerates
# its files occasionally; a mismatch is reported loudly rather than fatally,
# because the artifact records the hash actually used.
CORPUS_SHA256 = "2911dfcc2b0b498fe92ad9bd7e2c712046edb448eb6fe3bd669bcf9629adf8fd"

DEFAULT_SEED = ablation.DEFAULT_SEED
GEOMETRIES = ablation.GEOMETRIES
SIDES = GEOMETRIES + ("js-cooccurrence",)
PERCENTILE = 0.35        # the prototype's own default (autoThresholdPercentile)
# Second operating point, fixed before the run and from the node count alone.
# Thresholding at the p-th percentile makes p the edge density of the clustering
# graph, and a graph on n = 166 nodes is above its connectivity threshold
# ln(n)/n = 0.031 at any p the prototype would pick: p=0.35 cannot return
# anything but one component, for any embedding whose distances are not
# degenerate. p=0.01 is the grid point safely below ln(n)/n for both node sets
# used here (166 synsets, 259 types). No result informed the choice; it is
# arithmetic on n, and it is applied identically to all three sides.
PERCENTILE_SPARSE = 0.01
SWEEP = (0.002, 0.005, 0.01, 0.02, 0.03, 0.05, 0.075, 0.10, 0.15, 0.20, 0.35, 0.50)

# JS prototype defaults, for the co-occurrence baseline (bench.js:113-134)
JS_WINDOW = 3
JS_PROJECTION = "random"
JS_WEIGHTING = "uniform"
JS_EPS = 1e-8            # compressionTest.js:75


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #

def main(argv=None):
    args = _parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    if args.figure:
        return main_figure(args)
    if args.dims:
        return main_multi_dim(args)
    if args.dataset != "wordnet-mammals":
        raise SystemExit("the lemma -> synset mapping of Premise 2 is defined for "
                         "wordnet-mammals only")

    seeds = ablation.seed_set(args.seed, args.seeds)
    tag = ablation.seed_tag(args.seed, args.seeds)
    hierarchy = datasets.load(args.dataset, seed=args.seed)

    print(f"corpus: {CORPUS_TITLE}")
    text, corpus_sha, body_path = load_corpus(args)
    mapping = build_mapping(hierarchy, text, args)
    _write_json(os.path.join(args.out,
                             f"compress_mapping_pg{CORPUS_ID}_{args.dataset}.json"),
                {k: v for k, v in mapping.items() if k not in ("tokens", "freq")})
    report_mapping(mapping)
    if mapping["n_nodes"] < 2:
        raise SystemExit("fewer than two nodes in the intersection: nothing to cluster")

    js_vectors, js_cap = None, None
    if not args.no_js:
        js_vectors = {s: js_embedding(args, mapping, s, body_path) for s in seeds}
        js_cap = js_cap_diagnostic(args, mapping, seeds, body_path)

    runs = []
    for geometry in GEOMETRIES:
        for seed in seeds:
            coords = coordinates(geometry, args, hierarchy, seed)
            dist = subset_distances(geometry, coords, mapping["node_index"])
            runs.append(measure(geometry, dist, mapping, hierarchy, args, seed))
    if js_vectors is not None:
        for seed in seeds:
            dist = poincare_distances(js_vectors[seed], mapping)
            runs.append(measure("js-cooccurrence", dist, mapping, hierarchy, args, seed,
                                node_set="types"))

    for record in runs:
        _write_json(os.path.join(
            args.out, f"compress_run_{record['side']}_{args.dataset}"
                      f"_d{args.dim}_seed{record['seed']}.json"), record)

    aggregate = summarise(runs, mapping, args, seeds, tag, corpus_sha)
    aggregate["js_cap_diagnostic"] = js_cap
    paths = write_outputs(aggregate, args, tag)
    report(aggregate, paths, args, seeds, tag)
    return 0


# --------------------------------------------------------------------------- #
# Phase 5b (addendum) — the dimensional sweep, additive
# --------------------------------------------------------------------------- #

JS_REFERENCE_DIM = 2  # the js-cooccurrence side is carried forward from here
EXPECTED_N_TYPES_MAPPED = 259  # published Phase-5 mapping stats; see
EXPECTED_N_NODES = 166         # _check_mapping_invariant


def main_multi_dim(args):
    """Entry point for `--dims`: the existing pipeline, at several dimensions,
    with the three rules from the PHASE 5b docstring section enforced up front.
    """
    if args.dataset != "wordnet-mammals":
        raise SystemExit("the lemma -> synset mapping of Premise 2 is defined for "
                         "wordnet-mammals only")
    dims = sorted(set(args.dims))
    seeds = ablation.seed_set(args.seed, args.seeds)
    tag = ablation.seed_tag(args.seed, args.seeds)

    missing = _missing_checkpoints(dims, args.dataset, args.out, seeds)
    if missing:
        raise SystemExit(
            "missing Phase-3/Phase-4 embedding checkpoint(s); --dims does not "
            "substitute a fresh training run for a missing cell:\n  "
            + "\n  ".join(missing))
    js_runs = [] if args.no_js else _load_js_reference(args, seeds)

    hierarchy = datasets.load(args.dataset, seed=args.seed)
    print(f"corpus: {CORPUS_TITLE}")
    text, corpus_sha, body_path = load_corpus(args)
    mapping = build_mapping(hierarchy, text, args)
    _write_json(os.path.join(args.out,
                             f"compress_mapping_pg{CORPUS_ID}_{args.dataset}.json"),
                {k: v for k, v in mapping.items() if k not in ("tokens", "freq")})
    report_mapping(mapping)
    _check_mapping_invariant(mapping)
    if mapping["n_nodes"] < 2:
        raise SystemExit("fewer than two nodes in the intersection: nothing to cluster")

    per_dim = {}
    for dim in dims:
        print(f"\n=== d={dim} ===", flush=True)
        dim_args = argparse.Namespace(**vars(args))
        dim_args.dim = dim

        runs = []
        for geometry in GEOMETRIES:
            for seed in seeds:
                coords = coordinates(geometry, dim_args, hierarchy, seed)
                dist = subset_distances(geometry, coords, mapping["node_index"])
                runs.append(measure(geometry, dist, mapping, hierarchy, dim_args, seed))
        for record in runs:
            _write_json(os.path.join(
                dim_args.out, f"compress_run_{record['side']}_{dim_args.dataset}"
                              f"_d{dim}_seed{record['seed']}.json"), record)

        aggregate = summarise(runs + js_runs, mapping, dim_args, seeds, tag, corpus_sha)
        aggregate["js_cooccurrence_constant_by_construction"] = True
        aggregate["js_cooccurrence_source_dim"] = JS_REFERENCE_DIM
        paths = write_outputs(aggregate, dim_args, tag)
        report(aggregate, paths, dim_args, seeds, tag)

        ref = phase4_reference(dim, args.dataset, args.out, seeds)
        rankings = {_pkey(p): rank_by_gold_hops(aggregate, p)
                    for p in aggregate["operating_points"]}
        matches = {pkey: _ranking_verdict(ranking, ref)
                   for pkey, ranking in rankings.items()}
        per_dim[dim] = {
            "aggregate_paths": {k: v for k, v in paths.items()},
            "gold_hops_ranking": {
                pkey: [{"side": s, "gold_hops_token_weighted":
                        {"mean": m, "sigma": sg}} for s, m, sg in ranking]
                for pkey, ranking in rankings.items()},
            "phase4_reference": ref,
            "ranking_match": matches,
            "ratio_fidelity_correlation": ratio_fidelity_correlation(aggregate),
        }

    summary_paths = write_dims_summary(per_dim, args, dims, seeds, tag)
    report_dims(per_dim, args, dims, seeds, tag, summary_paths)
    return 0


def _missing_checkpoints(dims, dataset, out_dir, seeds):
    """Every (geometry, dim, seed) cell's Phase-4 checkpoint the sweep needs."""
    missing = []
    for dim in dims:
        for geometry in GEOMETRIES:
            for seed in seeds:
                path = os.path.join(
                    out_dir, f"ablation_run_{geometry}_{dataset}_d{dim}_seed{seed}.json")
                if not os.path.exists(path):
                    missing.append(path)
    return missing


def _load_js_reference(args, seeds):
    """The five Phase-5 js-cooccurrence per-seed records at d=2, unchanged.

    Carried forward rather than re-run: the packet designates this side a
    constant reference row, not a per-dimension measurement (see the module
    docstring). Fails loudly rather than silently re-running it if a record
    (or a percentile this run's --sweep needs) is missing.
    """
    runs, missing = [], []
    for seed in seeds:
        path = os.path.join(args.out, f"compress_run_js-cooccurrence_"
                                      f"{args.dataset}_d{JS_REFERENCE_DIM}_seed{seed}.json")
        if not os.path.exists(path):
            missing.append(path)
            continue
        with open(path, encoding="utf-8") as fh:
            record = json.load(fh)
        gaps = [p for p in args.sweep if _pkey(p) not in record["grid"]]
        if gaps:
            raise SystemExit(
                f"{path} has no grid entry for percentile(s) {gaps}; the "
                f"js-cooccurrence side is carried forward from d={JS_REFERENCE_DIM} "
                f"unchanged and cannot be re-measured at a different --sweep than "
                f"the one that produced it")
        runs.append(record)
    if missing:
        raise SystemExit(
            f"missing Phase-5 js-cooccurrence reference record(s) at "
            f"d={JS_REFERENCE_DIM} (--dims carries this side forward unchanged "
            f"rather than re-measuring it):\n  " + "\n  ".join(missing))
    return runs


def _check_mapping_invariant(mapping):
    """The lemma->synset mapping must be the same at every dimension.

    It is, by construction, here: `build_mapping` never reads `args.dim` and
    is called once and shared across the sweep. This is the second, independent
    check the packet asks for -- that today's mapping still matches the
    published Phase-5 figures, so a corpus/WordNet/logic drift is reported
    rather than silently producing a different-but-internally-consistent count.
    """
    got = (mapping["n_types_mapped"], mapping["n_nodes"])
    expected = (EXPECTED_N_TYPES_MAPPED, EXPECTED_N_NODES)
    if got != expected:
        raise SystemExit(
            f"mapping invariant broken: got {got[0]} mapped types / {got[1]} "
            f"nodes, expected {expected[0]}/{expected[1]} (the Phase-5 values). "
            f"The mapping is dimension-independent and must be identical at "
            f"every d; this mismatch means it is being rebuilt, which is a "
            f"defect -- stop and report it rather than continuing.")


def phase4_reference(dim, dataset, out_dir, seeds):
    """Phase-4 MAP and avg-distortion ranking, re-derived from the checkpoint
    files themselves (never transcribed from the README table)."""
    means = {}
    for geometry in GEOMETRIES:
        maps, dists = [], []
        for seed in seeds:
            path = os.path.join(
                out_dir, f"ablation_run_{geometry}_{dataset}_d{dim}_seed{seed}.json")
            with open(path, encoding="utf-8") as fh:
                record = json.load(fh)
            maps.append(record["map"])
            dists.append(record["avg_distortion"])
        means[geometry] = {"map": _mean_sigma(maps),
                           "avg_distortion": _mean_sigma(dists)}
    return {
        "means": means,
        "map_ranking": sorted(GEOMETRIES, key=lambda g: -means[g]["map"]["mean"]),
        "distortion_ranking": sorted(
            GEOMETRIES, key=lambda g: means[g]["avg_distortion"]["mean"]),
    }


def rank_by_gold_hops(aggregate, percentile):
    """Sides ordered by `gold_hops_token_weighted`, ascending (fewer hops =
    more semantically faithful clustering), at one operating point."""
    key = _pkey(percentile)
    entries = []
    for side in SIDES:
        entry = aggregate["sides"].get(side)
        if entry is None:
            continue
        cell = entry["grid"][key]["gold_hops_token_weighted"]
        entries.append((side, cell["mean"], cell["sigma"]))
    entries.sort(key=lambda e: e[1])
    return entries


def _ranking_verdict(gold_ranking, ref):
    """Does the euclidean-vs-lorentz slice of the gold-hops order match the
    Phase-4 MAP ranking, the distortion ranking, both, or neither."""
    order = [side for side, _, _ in gold_ranking if side in GEOMETRIES]
    matches_map = order == ref["map_ranking"]
    matches_distortion = order == ref["distortion_ranking"]
    if matches_map and matches_distortion:
        verdict = "both"
    elif matches_map:
        verdict = "map_only"
    elif matches_distortion:
        verdict = "distortion_only"
    else:
        verdict = "neither"
    return {
        "euclidean_vs_lorentz_gold_order": order,
        "matches_map_ranking": matches_map,
        "matches_distortion_ranking": matches_distortion,
        "verdict": verdict,
    }


def _pearson(xs, ys):
    x, y = np.asarray(xs, dtype=np.float64), np.asarray(ys, dtype=np.float64)
    if x.size < 2 or np.std(x) == 0.0 or np.std(y) == 0.0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def ratio_fidelity_correlation(aggregate):
    """The d=2 ratio-vs-fidelity anti-correlation, repeated at this dimension:
    Pearson r between `ratio` and (`gold_hops_token_weighted`,
    `largest_cluster_token_share`) over every (side, percentile) cell."""
    ratios, hops, shares = [], [], []
    for entry in aggregate["sides"].values():
        for cell in entry["grid"].values():
            ratios.append(cell["ratio"]["mean"])
            hops.append(cell["gold_hops_token_weighted"]["mean"])
            shares.append(cell["largest_cluster_token_share"]["mean"])
    return {
        "n_cells": len(ratios),
        "gold_hops": _pearson(ratios, hops),
        "largest_cluster_token_share": _pearson(ratios, shares),
    }


def write_dims_summary(per_dim, args, dims, seeds, tag):
    base = (f"compress_dims_{args.dataset}_dims"
            f"{'-'.join(str(d) for d in dims)}_{tag}")
    payload = {"dataset": args.dataset, "dims": dims, "seeds": seeds,
              "seed_tag": tag, "js_cooccurrence_source_dim": JS_REFERENCE_DIM,
              "per_dimension": {str(d): per_dim[d] for d in dims}}
    paths = {"json": os.path.join(args.out, base + ".json"),
             "md": os.path.join(args.out, base + ".md")}
    _write_json(paths["json"], payload)
    with open(paths["md"], "w", encoding="utf-8") as fh:
        fh.write(_dims_markdown(payload))
    return paths


def _dims_markdown(payload):
    out = [
        "# Phase 5b — the dimensional sweep of the compression pipeline\n",
        f"`{payload['dataset']}`, d in {payload['dims']}, seeds {payload['seeds']} "
        f"(`{payload['seed_tag']}`), mean ± σ over the seed set. The "
        f"js-cooccurrence side is carried forward unchanged from "
        f"d={payload['js_cooccurrence_source_dim']} (dimension-independent by "
        f"construction; not re-measured here).\n",
    ]
    for dim in payload["dims"]:
        entry = payload["per_dimension"][str(dim)]
        out.append(f"\n## d = {dim}\n")
        for pkey, ranking in entry["gold_hops_ranking"].items():
            out.append(f"\n### auto-threshold percentile p = {pkey}\n")
            out.append("| rank | side | gold hops (token-weighted) |")
            out.append("|---|---|---|")
            for i, row in enumerate(ranking, 1):
                stat = row["gold_hops_token_weighted"]
                out.append(f"| {i} | {row['side']} | "
                          f"{stat['mean']:.3f} ± {stat['sigma']:.3f} |")
            verdict = entry["ranking_match"][pkey]
            order = " > ".join(verdict["euclidean_vs_lorentz_gold_order"])
            out.append(f"\nEuclidean-vs-Lorentz gold-hops order (fewer hops "
                      f"first): {order}. Matches Phase-4 MAP ranking: "
                      f"{verdict['matches_map_ranking']}. Matches Phase-4 "
                      f"distortion ranking: {verdict['matches_distortion_ranking']}. "
                      f"Verdict: **{verdict['verdict']}**.\n")
        ref = entry["phase4_reference"]
        m = ref["means"]
        out.append(
            f"\nPhase-4 reference at d={dim} (re-derived from the checkpoints): "
            f"MAP euclidean {m['euclidean']['map']['mean']:.4f} ± "
            f"{m['euclidean']['map']['sigma']:.4f} vs lorentz "
            f"{m['lorentz']['map']['mean']:.4f} ± {m['lorentz']['map']['sigma']:.4f} "
            f"(ranking {' > '.join(ref['map_ranking'])}, higher first); avg "
            f"distortion euclidean {m['euclidean']['avg_distortion']['mean']:.4f} "
            f"± {m['euclidean']['avg_distortion']['sigma']:.4f} vs lorentz "
            f"{m['lorentz']['avg_distortion']['mean']:.4f} ± "
            f"{m['lorentz']['avg_distortion']['sigma']:.4f} (ranking "
            f"{' < '.join(ref['distortion_ranking'])}, lower first).\n")
        corr = entry["ratio_fidelity_correlation"]
        out.append(
            f"\nRatio-vs-fidelity correlation at d={dim}, over {corr['n_cells']} "
            f"(side, percentile) cells: r(ratio, gold hops) = "
            f"{corr['gold_hops']:.3f}; r(ratio, largest-cluster token share) = "
            f"{corr['largest_cluster_token_share']:.3f}. Phase-5 reference "
            f"(d=2, 36 cells): -0.88 / -0.92.\n")
        out.append(f"\nFull aggregate: `{entry['aggregate_paths']['json']}`, "
                  f"`{entry['aggregate_paths']['md']}`.\n")
    return "\n".join(out)


def report_dims(per_dim, args, dims, seeds, tag, summary_paths):
    """Console output is ASCII: this stdout is cp1252 and 'σ' raises there."""
    print()
    print(f"=== Phase 5b - {args.dataset} dims {dims}, seeds {seeds} ({tag}) ===")
    for dim in dims:
        entry = per_dim[dim]
        print(f"\n-- d={dim}")
        for pkey, ranking in entry["gold_hops_ranking"].items():
            row_text = "  >  ".join(
                f"{row['side']} {row['gold_hops_token_weighted']['mean']:.3f}"
                f"+/-{row['gold_hops_token_weighted']['sigma']:.3f}"
                for row in ranking)
            print(f"  p={pkey}: {row_text}")
            verdict = entry["ranking_match"][pkey]
            order = " > ".join(verdict["euclidean_vs_lorentz_gold_order"])
            print(f"    euclidean-vs-lorentz gold order: {order}   "
                  f"matches MAP: {verdict['matches_map_ranking']}   "
                  f"matches distortion: {verdict['matches_distortion_ranking']}   "
                  f"verdict: {verdict['verdict']}")
        m = entry["phase4_reference"]["means"]
        print(f"  Phase-4 ref: MAP eucl {m['euclidean']['map']['mean']:.4f} vs "
              f"lorentz {m['lorentz']['map']['mean']:.4f}   distortion eucl "
              f"{m['euclidean']['avg_distortion']['mean']:.4f} vs lorentz "
              f"{m['lorentz']['avg_distortion']['mean']:.4f}")
        corr = entry["ratio_fidelity_correlation"]
        print(f"  ratio-vs-fidelity corr (n={corr['n_cells']}): gold_hops "
              f"{corr['gold_hops']:.3f}   largest_cluster_share "
              f"{corr['largest_cluster_token_share']:.3f}   "
              f"(Phase-5 d=2, n=36: -0.88 / -0.92)")
    print()
    for name, path in summary_paths.items():
        print(f"  {name}: {path}")
    print()
    print("regenerate:")
    print(f"  python compress.py --dataset {args.dataset} --dims "
          f"{' '.join(str(d) for d in dims)} --seeds {args.seeds} "
          f"--out {args.out}")


# --------------------------------------------------------------------------- #
# step 1 — the corpus and its tokens
# --------------------------------------------------------------------------- #

def load_corpus(args):
    """Fetch (once) and cache the corpus in `--out`; return (body, sha256, path).

    Only the text between Project Gutenberg's `*** START OF` / `*** END OF`
    markers is used: the licence boilerplate is not part of Darwin's vocabulary.
    The body is written back out as its own file because the JS prototype is
    handed a path, and it must read exactly the text Python read — the token
    counts are compared, and the boilerplate alone is 2955 tokens.
    """
    path = args.corpus_file or os.path.join(args.out, f"compress_corpus_pg{CORPUS_ID}.txt")
    if not os.path.exists(path):
        print(f"  fetching {CORPUS_URL}", flush=True)
        with urllib.request.urlopen(CORPUS_URL, timeout=60) as response:
            raw = response.read()
        with open(path, "wb") as fh:
            fh.write(raw)
    with open(path, "rb") as fh:
        raw = fh.read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != CORPUS_SHA256:
        print(f"  WARNING: corpus sha256 {sha[:16]}... != pinned "
              f"{CORPUS_SHA256[:16]}...; the numbers below are for the file on disk")
    text = raw.decode("utf-8", errors="replace")
    start = text.find("*** START OF")
    start = text.find("\n", start) + 1 if start >= 0 else 0
    end = text.find("*** END OF")
    end = end if end >= 0 else len(text)
    body = text[start:end]
    body_path = os.path.join(args.out, f"compress_corpus_pg{CORPUS_ID}_body.txt")
    with open(body_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    print(f"  {path}  sha256 {sha[:16]}...  body {len(body)} chars "
          f"-> {os.path.basename(body_path)}")
    return body, sha, body_path


def tokenize(text):
    """Port of `compressionTest.js:90-95`: NFKC, lowercase, /\\p{L}{2,}/gu.

    `str.isalpha()` is true for exactly the Unicode categories `\\p{L}` matches,
    so grouping the string into maximal alphabetic runs and keeping those of
    length >= 2 is the same token stream the regex produces. The JS is asked to
    confirm it (`js_embedding`).
    """
    lowered = unicodedata.normalize("NFKC", text).lower()
    out = []
    for is_alpha, run in groupby(lowered, key=str.isalpha):
        if not is_alpha:
            continue
        token = "".join(run)
        if len(token) >= 2:
            out.append(token)
    return out


# --------------------------------------------------------------------------- #
# Premise 2 — lemma -> synset, with the ambiguity in the open
# --------------------------------------------------------------------------- #

def build_mapping(hierarchy, text, args):
    """Map the corpus vocabulary onto subtree synsets. Geometry-independent."""
    from nltk.corpus import wordnet as wn

    lemma_to_names = {}
    multiword = 0
    for name in hierarchy.names:
        for lemma in wn.synset(name).lemma_names():
            key = lemma.lower()
            if "_" in key:
                multiword += 1
                continue
            lemma_to_names.setdefault(key, []).append(name)

    tokens = tokenize(text)
    freq = Counter(tokens)
    ordered = sorted(freq, key=lambda w: (-freq[w], w))
    vocabulary = ordered[:args.max_vocab] if args.max_vocab else ordered

    node_of_name = {name: i for i, name in enumerate(hierarchy.names)}
    resolved, bases, morphy_only, ambiguous = {}, {}, 0, 0
    for word in vocabulary:
        base, candidates = word, lemma_to_names.get(word)
        if candidates is None:
            morphed = wn.morphy(word, wn.NOUN)
            if morphed and morphed.lower() in lemma_to_names:
                base = morphed.lower()
                candidates = lemma_to_names[base]
                morphy_only += 1
        if not candidates:
            continue
        if len(candidates) > 1:
            ambiguous += 1
        resolved[word] = _resolve(wn, base, candidates, node_of_name)
        bases[word] = base

    nodes = sorted({resolved[w] for w in resolved})
    encoded = sum(freq[w] for w in resolved)
    eligible = sum(freq[w] for w in vocabulary)
    dominant = sum(freq[w] for w in resolved
                   if _dominant_sense_in_subtree(wn, bases[w], node_of_name))

    # Entropy of the mapped type distribution. Not a competing code — the
    # accounting stays fixed-width, per the non-goals — but the honest reference
    # for how much of `size_before` is the fixed-width code's own slack.
    entropy = 0.0
    for word in resolved:
        p = freq[word] / max(encoded, 1)
        if p > 0:
            entropy -= p * math.log2(p)

    # types sharing a synset ("dog"/"dogs", synonyms) are one point in a Route-A
    # embedding, so this collapse happens before any geometry does anything.
    return {
        "type_entropy_bits": entropy,
        "corpus": CORPUS_TITLE,
        "corpus_url": CORPUS_URL,
        "max_vocab": args.max_vocab or None,
        "n_tokens_total": len(tokens),
        "n_types_total": len(freq),
        "n_types_eligible": len(vocabulary),
        "n_tokens_eligible": eligible,
        "subtree_nodes": hierarchy.n,
        "multiword_lemmas_skipped": multiword,
        "single_word_lemma_keys": len(lemma_to_names),
        "n_types_mapped": len(resolved),
        "n_types_morphy_only": morphy_only,
        "n_types_ambiguous_in_subtree": ambiguous,
        "n_nodes": len(nodes),
        "node_coverage_fraction": len(nodes) / hierarchy.n,
        "n_tokens_encoded": encoded,
        "n_tokens_dropped_unmapped": eligible - encoded,
        "token_coverage_fraction": encoded / max(eligible, 1),
        "dominant_sense_token_fraction": dominant / max(encoded, 1),
        "node_index": nodes,                     # hierarchy indices, ascending
        "type_to_node": resolved,                # word -> hierarchy index
        "freq": {w: freq[w] for w in resolved},  # token counts of mapped types
        "vocabulary": sorted(resolved),          # canonical order of the code
    }


def _resolve(wn, base, candidates, node_of_name):
    """Lowest WordNet sense number of `base` among `candidates`; BFS index breaks
    ties. Deterministic, and it prefers the frequent reading of an ambiguous
    lemma ("bull" the bovine over "bull" the elephant seal)."""
    senses = [s.name() for s in wn.synsets(base, wn.NOUN)]
    ranked = []
    for name in candidates:
        order = senses.index(name) if name in senses else len(senses)
        ranked.append((order, node_of_name[name]))
    return min(ranked)[1]


def _dominant_sense_in_subtree(wn, base, node_of_name):
    senses = wn.synsets(base, wn.NOUN)
    return bool(senses) and senses[0].name() in node_of_name


def report_mapping(m):
    print(f"  tokens {m['n_tokens_total']}  types {m['n_types_total']}"
          f"  eligible types {m['n_types_eligible']}"
          f" (max_vocab {m['max_vocab']})")
    print(f"  mapped types {m['n_types_mapped']}"
          f" (morphy-only {m['n_types_morphy_only']},"
          f" ambiguous in subtree {m['n_types_ambiguous_in_subtree']})"
          f"  -> nodes {m['n_nodes']}/{m['subtree_nodes']}"
          f" ({100 * m['node_coverage_fraction']:.1f}% of the hierarchy)")
    print(f"  tokens encoded {m['n_tokens_encoded']}"
          f"  dropped as unmapped {m['n_tokens_dropped_unmapped']}"
          f"  ({100 * m['token_coverage_fraction']:.2f}% encoded)")
    print(f"  mapped tokens whose dominant WordNet noun sense is in the subtree: "
          f"{100 * m['dominant_sense_token_fraction']:.1f}%")
    print()


# --------------------------------------------------------------------------- #
# the learned coordinates: re-train once, persist, gate against Phase 4
# --------------------------------------------------------------------------- #

def coordinates(geometry, args, hierarchy, seed):
    """Coordinates for (geometry, dim, seed), from cache or freshly trained.

    Training reproduces `ablation.run_once`'s scoring path exactly — the sealed
    seeding-and-building order — because the point of the gate below is that
    these are the same coordinates the Phase-4 table was computed from.
    """
    path = os.path.join(args.out, f"compress_coords_{geometry}_{args.dataset}"
                                  f"_d{args.dim}_seed{seed}.npz")
    module = importlib.import_module(f"embeddings.{geometry}")
    lr = ablation._learning_rate(geometry, args.dim)

    if os.path.exists(path):
        stored = np.load(path, allow_pickle=False)
        if int(stored["epochs"]) == ablation.EPOCHS and float(stored["lr"]) == lr:
            coords = stored["coords"]
            print(f"  {geometry} seed={seed}: coordinates cached", flush=True)
            gate(geometry, args, hierarchy, coords, module, seed)
            return coords

    print(f"  {geometry} seed={seed}: training (lr={lr}, "
          f"{ablation.EPOCHS} epochs)", flush=True)
    started = time.perf_counter()
    np.random.seed(seed)
    torch.manual_seed(seed)
    with ablation._hyperparams(module, lr, ablation.EPOCHS):
        coords, _ = module.build(hierarchy, args.dim, seed)
    np.savez(path, coords=np.asarray(coords, dtype=np.float64),
             lr=np.float64(lr), epochs=np.int64(ablation.EPOCHS),
             dim=np.int64(args.dim), seed=np.int64(seed))
    print(f"    {time.perf_counter() - started:.0f}s -> {os.path.basename(path)}",
          flush=True)
    gate(geometry, args, hierarchy, coords, module, seed)
    return coords


def gate(geometry, args, hierarchy, coords, module, seed):
    """The coordinates must score exactly what the Phase-4 checkpoint recorded.

    Without this the compression numbers could be computed from an embedding
    that merely resembles the published one.
    """
    path = os.path.join(args.out, f"ablation_run_{geometry}_{args.dataset}"
                                  f"_d{args.dim}_seed{seed}.json")
    if not os.path.exists(path):
        print(f"    gate skipped: no Phase-4 checkpoint at {os.path.basename(path)}")
        return
    with open(path, encoding="utf-8") as fh:
        reference = json.load(fh)
    scored = metrics.evaluate(hierarchy, full_distances(module, coords))
    worst = 0.0
    for key in ("map", "mean_rank", "avg_distortion"):
        worst = max(worst, abs(scored[key] - reference[key]))
    if worst > ablation.GATE_TOL:
        raise SystemExit(
            f"gate FAILED for {geometry} d={args.dim} seed={seed}: MAP "
            f"{scored['map']:.6f} vs {reference['map']:.6f}, rank "
            f"{scored['mean_rank']:.6f} vs {reference['mean_rank']:.6f}, distortion "
            f"{scored['avg_distortion']:.6f} vs {reference['avg_distortion']:.6f} "
            f"(max delta {worst:.2e} > {ablation.GATE_TOL:.0e}). These are not the "
            f"coordinates the Phase-4 table describes; stop.")
    print(f"    gate ok: MAP {scored['map']:.4f}  rank {scored['mean_rank']:.4f}  "
          f"distortion {scored['avg_distortion']:.4f}  (max delta {worst:.1e})")


def full_distances(module, coords):
    """(n, n) distances via the sealed module's own `_pairwise`, symmetrised and
    zero-diagonalled the way its `build` does."""
    with torch.no_grad():
        dist = module._pairwise(torch.as_tensor(np.asarray(coords), dtype=torch.float64))
        dist = 0.5 * (dist + dist.T)
        dist.fill_diagonal_(0.0)
    return dist.numpy()


def subset_distances(geometry, coords, node_index):
    """Distances among the clustered nodes only, same `_pairwise` as above.

    Pairwise distances carry no global normalisation, so the submatrix of the
    full matrix and the matrix of the subset are the same numbers.
    """
    module = importlib.import_module(f"embeddings.{geometry}")
    return full_distances(module, np.asarray(coords)[node_index])


# --------------------------------------------------------------------------- #
# the JS co-occurrence baseline: the prototype's own embedding, unedited
# --------------------------------------------------------------------------- #

JS_SCRIPT = r"""
const fs = require('fs');
// `node -e script -- a b` puts a at argv[1] and b at argv[2] (no script path).
const H = require(process.argv[1]);
const opts = JSON.parse(process.argv[2]);
const text = fs.readFileSync(opts.corpus, 'utf8');
const want = new Set(JSON.parse(fs.readFileSync(opts.wantFile, 'utf8')));
const c = new H(opts.dimension, {
  seed: opts.seed, maxVocab: opts.maxVocab, windowSize: opts.windowSize,
  projection: opts.projection, weighting: opts.weighting, randomFeaturesPerDim: 16,
  normalize: true, verbose: false,
});
const words = c.preprocessText(text);
const built = c.createCooccurrenceMatrix(words, c.windowSize);
const emb = c.embedInHyperbolic(built.matrix);
const out = { tokens: words.length, vocab: built.uniqueWords.length, vectors: {} };
for (let i = 0; i < built.uniqueWords.length; i++) {
  if (want.has(built.uniqueWords[i])) out.vectors[built.uniqueWords[i]] = emb[i];
}
process.stdout.write(JSON.stringify(out));
"""


def js_cap_diagnostic(args, mapping, seeds, body_path):
    """Is the JS side's distance collapse an artefact of the uncapped vocabulary?

    The baseline is run at `--max-vocab 0` so that all 259 mapped types exist in
    its vocabulary and the three sides encode the same token stream. That is not
    the prototype's default (`maxVocab: 5000`), and a sparser co-occurrence
    matrix is exactly the condition under which its 16-random-features projection
    sends empty rows to the origin. So the same measurement is repeated at the
    prototype's own cap, over whichever mapped types survive it, and reported as
    a footnote: if the collapse is still there, the uncapped run did not cause it.
    """
    capped = argparse.Namespace(**vars(args))
    capped.max_vocab = 5000
    fractions, present = [], []
    for seed in seeds:
        vectors = js_embedding(capped, mapping, seed, body_path, require_all=False)
        words = [w for w in mapping["vocabulary"] if w in vectors]
        if len(words) < 2:
            continue
        subset = dict(mapping, vocabulary=words)
        dist = poincare_distances(vectors, subset)
        pairs = dist[np.triu_indices(dist.shape[0], 1)]
        fractions.append(float((pairs <= 0.0).mean()))
        present.append(len(words))
    if not fractions:
        return None
    return {"max_vocab": 5000, "types_present": _mean_sigma(present),
            "zero_pair_fraction": _mean_sigma(fractions)}


def js_embedding(args, mapping, seed, body_path, require_all=True):
    """Steps 1-4 of the prototype, run by the prototype, for one seed.

    `node -e` on the documented public methods (`preprocessText`,
    `createCooccurrenceMatrix`, `embedInHyperbolic`), called in the order
    `analyzeAndCompress` calls them so the internal LCG sees the same sequence.
    Its clustering is deliberately *not* used: the comparison must differ in the
    coordinates alone, so steps 5-8 are the same Python code for all three sides.
    """
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    want_file = os.path.join(args.out, f"compress_js_wanted_seed{seed}.json")
    _write_json(want_file, mapping["vocabulary"])
    payload = {
        "corpus": os.path.abspath(body_path),
        # node runs with cwd = repo root, so both paths must be absolute
        "wantFile": os.path.abspath(want_file), "seed": seed, "dimension": args.dim,
        "maxVocab": args.max_vocab or 10 ** 9, "windowSize": JS_WINDOW,
        "projection": JS_PROJECTION, "weighting": JS_WEIGHTING,
    }
    print(f"  js-cooccurrence seed={seed}: node -e (dimension {args.dim}, "
          f"projection {JS_PROJECTION}, window {JS_WINDOW})", flush=True)
    completed = subprocess.run(
        ["node", "-e", JS_SCRIPT, "--",
         os.path.join(root, "compressionTest.js"), json.dumps(payload)],
        capture_output=True, text=True, cwd=root, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"the JS prototype failed:\n{completed.stderr.strip()}")
    result = json.loads(completed.stdout)

    # Cross-check of the tokeniser port: same corpus, same token count, or the
    # Python side is not reading the text the prototype reads.
    if result["tokens"] != mapping["n_tokens_total"]:
        raise SystemExit(
            f"tokeniser mismatch: JS {result['tokens']} tokens, "
            f"Python {mapping['n_tokens_total']}. The port of "
            f"compressionTest.js:90-95 is wrong; stop.")
    missing = [w for w in mapping["vocabulary"] if w not in result["vectors"]]
    if missing and require_all:
        raise SystemExit(f"{len(missing)} mapped types absent from the JS "
                         f"vocabulary (e.g. {missing[:5]}): raise --max-vocab")
    return result["vectors"]


def poincare_distances(vectors, mapping):
    """The prototype's Poincaré distance (`compressionTest.js:294-313`), over the
    mapped types in the code's canonical order."""
    x = np.array([vectors[w] for w in mapping["vocabulary"]], dtype=np.float64)
    norm2 = (x * x).sum(axis=1)
    diff2 = (norm2[:, None] + norm2[None, :] - 2.0 * (x @ x.T)).clip(min=0.0)
    denom = np.maximum(1.0 - norm2, JS_EPS)
    argument = 1.0 + 2.0 * diff2 / (denom[:, None] * denom[None, :])
    return np.arccosh(np.maximum(argument, 1.0))


# --------------------------------------------------------------------------- #
# steps 6-7 — threshold and union-find
# --------------------------------------------------------------------------- #

def auto_threshold(dist, percentile):
    """The prototype's `percentile` auto-threshold, exact over all pairs.

    Index convention copied from `compressionTest.js:499-503`:
    `floor(p * (len - 1))` on the ascending sample.
    """
    pairs = np.sort(dist[np.triu_indices(dist.shape[0], 1)])
    if pairs.size == 0:
        return 0.0
    index = int(min(max(math.floor(percentile * (pairs.size - 1)), 0), pairs.size - 1))
    return float(min(max(pairs[index], 1e-6), 10.0))  # the JS clamp


def cluster(dist, threshold):
    """Connected components of `d < threshold` (union-find, path compression).

    `compressionTest.js:575-659` with `clusterK = 0`: full pairwise, strict <.
    """
    n = dist.shape[0]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    rows, cols = np.where(np.triu(dist < threshold, 1))
    for i, j in zip(rows.tolist(), cols.tolist()):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)  # union by index, as the JS does
    labels = np.array([find(i) for i in range(n)], dtype=np.int64)
    _, compact = np.unique(labels, return_inverse=True)
    return compact


# --------------------------------------------------------------------------- #
# step 8 — the stated code, and what it destroys
# --------------------------------------------------------------------------- #

def measure(side, dist, mapping, hierarchy, args, seed, node_set="nodes"):
    """One (side, seed) cell: threshold, cluster, count bits, measure the loss.

    `node_set` says what a row of `dist` is. The learned sides embed *synsets*,
    so their rows are the 166 nodes and every type sharing a synset is already
    one point; the JS side embeds *words*, so its rows are the 259 types. The
    accounting alphabet is the same either way — the mapped token stream — which
    is what makes the ratios comparable, and the difference is stated rather
    than smoothed over.
    """
    vocabulary = mapping["vocabulary"]
    if node_set == "nodes":
        row_of = {node: i for i, node in enumerate(mapping["node_index"])}
        row_of_type = {w: row_of[mapping["type_to_node"][w]] for w in vocabulary}
    else:
        row_of_type = {w: i for i, w in enumerate(vocabulary)}

    grid = {}
    for percentile in args.sweep:
        threshold = auto_threshold(dist, percentile)
        cell = accounting(cluster(dist, threshold), row_of_type, mapping, hierarchy)
        cell["threshold"] = threshold
        cell["percentile"] = percentile
        grid[_pkey(percentile)] = cell

    pairs = dist[np.triu_indices(dist.shape[0], 1)]
    record = {
        "side": side, "dataset": args.dataset, "dim": args.dim, "seed": seed,
        "node_set": node_set, "n_rows": int(dist.shape[0]),
        # why a threshold can land on the prototype's 1e-6 clamp: coincident
        # points. The heuristic co-occurrence embedding produces them in bulk
        # (identical sparse rows project to identical vectors); a trained one
        # should not.
        "zero_pair_fraction": float((pairs <= 0.0).mean()),
        "pair_distance_median": float(np.median(pairs)),
        "grid": grid,
    }
    for percentile in _operating_points(args):
        cell = grid[_pkey(percentile)]
        print(f"    {side:<15} seed={seed} p={percentile:<5} "
              f"threshold={cell['threshold']:.6f} clusters={cell['n_clusters']:<4} "
              f"ratio={cell['ratio']:.4f}  loss: "
              f"{100 * cell['collapsed_token_fraction']:.1f}% of tokens, "
              f"{cell['residual_bits_per_token']:.3f} bits/token", flush=True)
    return record


def accounting(labels, row_of_type, mapping, hierarchy):
    """Bits under THE CODE (module docstring), plus the measured loss."""
    freq = mapping["freq"]
    vocabulary = mapping["vocabulary"]
    n_tokens = mapping["n_tokens_encoded"]
    n_types = len(vocabulary)

    cluster_of = {w: int(labels[row_of_type[w]]) for w in vocabulary}
    n_clusters = len(set(cluster_of.values()))

    before = n_tokens * _bits(n_types)
    after = n_tokens * _bits(n_clusters) + n_types * _bits(n_clusters)
    ideal_before = n_tokens * math.log2(max(n_types, 1))
    ideal_after = (n_tokens + n_types) * math.log2(max(n_clusters, 1))

    members = {}
    for word, cid in cluster_of.items():
        members.setdefault(cid, []).append(word)

    collapsed = sum(freq[w] for cid, words in members.items() if len(words) > 1
                    for w in words)
    residual = 0.0
    for words in members.values():
        mass = sum(freq[w] for w in words)
        if mass == 0:
            continue
        for w in words:
            p = freq[w] / mass
            if p > 0:
                residual -= (mass / n_tokens) * p * math.log2(p)

    hops, weights, hops_max = 0.0, 0, 0.0
    for words in members.values():
        synsets = sorted({mapping["type_to_node"][w] for w in words})
        if len(synsets) < 2:
            continue
        pairs = [float(hierarchy.graph_dist[a, b])
                 for i, a in enumerate(synsets) for b in synsets[i + 1:]]
        mass = sum(freq[w] for w in words)
        hops += mass * (sum(pairs) / len(pairs))
        weights += mass
        hops_max = max(hops_max, max(pairs))

    return {
        "n_clusters": n_clusters,
        "n_tokens_encoded": n_tokens,
        "n_tokens_dropped_unmapped": mapping["n_tokens_dropped_unmapped"],
        "n_types": n_types,
        "bits_per_token_before": _bits(n_types),
        "bits_per_token_after": _bits(n_clusters),
        "size_before_bits": before,
        "size_after_bits": after,
        "ratio": after / before if before else 0.0,
        "ratio_ideal": ideal_after / ideal_before if ideal_before else 0.0,
        "ratio_prototype_units": (n_clusters + 0.5 * n_types) / max(n_tokens, 1),
        "collapsed_token_fraction": collapsed / max(n_tokens, 1),
        "residual_bits_per_token": residual,
        "gold_hops_token_weighted": hops / weights if weights else 0.0,
        "gold_hops_max": hops_max,
        "largest_cluster_token_share": max(
            (sum(freq[w] for w in words) for words in members.values()), default=0
        ) / max(n_tokens, 1),
        "largest_cluster_types": max((len(w) for w in members.values()), default=0),
        "singleton_clusters": sum(1 for w in members.values() if len(w) == 1),
    }


def _bits(symbols):
    """Fixed-width code length. One symbol needs no bits, and a ratio of 0.0 is
    then the honest arithmetic: everything has been thrown away."""
    return int(math.ceil(math.log2(symbols))) if symbols > 1 else 0


# --------------------------------------------------------------------------- #
# aggregate, artifacts, report
# --------------------------------------------------------------------------- #

FIELDS = ("n_clusters", "threshold", "ratio", "ratio_ideal",
          "ratio_prototype_units", "bits_per_token_after",
          "collapsed_token_fraction", "residual_bits_per_token",
          "gold_hops_token_weighted", "gold_hops_max",
          "largest_cluster_token_share", "singleton_clusters",
          "size_before_bits", "size_after_bits")


def summarise(runs, mapping, args, seeds, tag, corpus_sha):
    by_side = {}
    for side in SIDES:
        cells = [r for r in runs if r["side"] == side]
        if not cells:
            continue
        by_side[side] = {
            "node_set": cells[0]["node_set"],
            "n_rows": cells[0]["n_rows"],
            "zero_pair_fraction": _mean_sigma([c["zero_pair_fraction"] for c in cells]),
            "pair_distance_median": _mean_sigma(
                [c["pair_distance_median"] for c in cells]),
            "grid": {_pkey(p): {f: _mean_sigma([c["grid"][_pkey(p)][f] for c in cells])
                                for f in FIELDS} for p in args.sweep},
        }

    floor_types = len(mapping["vocabulary"])
    floor_nodes = mapping["n_nodes"]
    return {
        "dataset": args.dataset, "dim": args.dim,
        "operating_points": list(_operating_points(args)),
        "percentile_grid": list(args.sweep),
        "seeds": seeds, "seed_tag": tag, "epochs": ablation.EPOCHS,
        "learning_rates": {g: ablation._learning_rate(g, args.dim) for g in GEOMETRIES},
        "corpus": {"title": CORPUS_TITLE, "url": CORPUS_URL, "sha256": corpus_sha},
        "code": ("size_before = N*ceil(log2 V); size_after = N*ceil(log2 K) + "
                 "V*ceil(log2 K); ratio = after/before; N = mapped tokens, "
                 "V = mapped types, K = clusters; fixed-width, no entropy coder"),
        "mapping": {k: v for k, v in mapping.items()
                    if k not in ("node_index", "type_to_node", "freq", "vocabulary")},
        "ratio_at_no_clustering": (
            (mapping["n_tokens_encoded"] + floor_types) * _bits(floor_nodes)
            / (mapping["n_tokens_encoded"] * _bits(floor_types))),
        "sides": by_side,
        "graph_diameter": float(np.max(datasets.load(args.dataset).graph_dist)),
    }


def _mean_sigma(values):
    array = np.asarray(values, dtype=np.float64)
    return {"mean": float(array.mean()), "sigma": float(array.std(ddof=0))}


def write_outputs(aggregate, args, tag):
    base = f"compress_{args.dataset}_d{args.dim}_{tag}"
    paths = {"json": os.path.join(args.out, base + ".json"),
             "md": os.path.join(args.out, base + ".md")}
    _write_json(paths["json"], aggregate)
    with open(paths["md"], "w", encoding="utf-8") as fh:
        fh.write(_markdown(aggregate, args, tag))
    paths["png"] = _plot(aggregate, args, tag)
    return paths


def _markdown(aggregate, args, tag):
    mapping = aggregate["mapping"]
    out = [f"# Phase 5 — the compression pipeline on the learned embeddings\n",
           f"`{args.dataset}`, d={args.dim}, seeds {aggregate['seeds']} (`{tag}`), "
           f"mean ± σ over the seed set.\n",
           f"Corpus: {aggregate['corpus']['title']}, sha256 "
           f"`{aggregate['corpus']['sha256'][:16]}…`. "
           f"N (tokens encoded) = {mapping['n_tokens_encoded']}, "
           f"V (mapped types) = {mapping['n_types_mapped']}, "
           f"dropped as unmapped = {mapping['n_tokens_dropped_unmapped']}, "
           f"nodes = {mapping['n_nodes']}/{mapping['subtree_nodes']}.\n",
           f"Code: {aggregate['code']}\n"]
    for percentile in aggregate["operating_points"]:
        out.append(f"\n## Auto-threshold percentile p = {percentile}\n")
        out.append("| side | clusters | tokens encoded | tokens dropped | "
                   "size before (bits) | size after (bits) | ratio |")
        out.append("|---|---|---|---|---|---|---|")
        for side, entry in aggregate["sides"].items():
            cell = entry["grid"][_pkey(percentile)]
            out.append(f"| {side} | {_pm(cell['n_clusters'], 2)} | "
                       f"{mapping['n_tokens_encoded']} | "
                       f"{mapping['n_tokens_dropped_unmapped']} | "
                       f"{_pm(cell['size_before_bits'], 0)} | "
                       f"{_pm(cell['size_after_bits'], 0)} | "
                       f"{_pm(cell['ratio'], 4)} |")
        out.append("")
        out.append("| side | collapsed tokens | residual bits/token | gold hops "
                   "(token-weighted) | gold hops max | largest cluster (token share) |")
        out.append("|---|---|---|---|---|---|")
        for side, entry in aggregate["sides"].items():
            cell = entry["grid"][_pkey(percentile)]
            out.append(f"| {side} | {_pm(cell['collapsed_token_fraction'], 4)} | "
                       f"{_pm(cell['residual_bits_per_token'], 3)} | "
                       f"{_pm(cell['gold_hops_token_weighted'], 2)} | "
                       f"{_pm(cell['gold_hops_max'], 1)} | "
                       f"{_pm(cell['largest_cluster_token_share'], 4)} |")
    out.append(f"\nMapping floor, no geometry involved (K = {mapping['n_nodes']} "
               f"synsets for V = {mapping['n_types_mapped']} types): ratio "
               f"{aggregate['ratio_at_no_clustering']:.4f}. Gold hops are measured "
               f"in the frozen hierarchy, whose diameter is "
               f"{aggregate['graph_diameter']:.0f} hops. The stated code spends "
               f"{_bits(mapping['n_types_mapped'])} bits/token before clustering "
               f"against an entropy of {mapping['type_entropy_bits']:.3f} "
               f"bits/token for the same type distribution — the fixed-width "
               f"code's own slack, identical on every side.\n")
    return "\n".join(out)


def _pm(stat, digits):
    return f"{stat['mean']:.{digits}f} ± {stat['sigma']:.{digits}f}"


def _plot(aggregate, args, tag):
    """Ratio, cluster count and destroyed-token share against the auto-threshold
    percentile, mean ± σ over the seed set. Never a single seed (CLAUDE.md)."""
    path = os.path.join(args.out, f"compress_ratio_vs_percentile_{args.dataset}"
                                  f"_d{args.dim}_{tag}.png")
    panels = (("ratio", "ratio (stated code)", False),
              ("n_clusters", "clusters K", True),
              ("collapsed_token_fraction", "tokens whose type is lost", False))
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    xs = np.array(args.sweep, dtype=np.float64)
    for side, entry in aggregate["sides"].items():
        for axis, (key, label, logy) in zip(axes, panels):
            mean = np.array([entry["grid"][_pkey(p)][key]["mean"] for p in args.sweep])
            sigma = np.array([entry["grid"][_pkey(p)][key]["sigma"] for p in args.sweep])
            axis.plot(xs, mean, marker="o", markersize=3.5, label=side)
            axis.fill_between(xs, mean - sigma, mean + sigma, alpha=0.2)
            axis.set_xlabel("auto-threshold percentile")
            axis.set_ylabel(label)
            axis.set_xscale("log")
            if logy:
                axis.set_yscale("log")
    for axis in axes:
        for percentile in aggregate["operating_points"]:
            axis.axvline(percentile, color="grey", linestyle=":", linewidth=1)
    axes[0].legend(fontsize=8)
    fig.suptitle(f"{args.dataset} d={args.dim} — semantic-compression ratio, cluster "
                 f"count and destroyed vocabulary vs the auto-threshold percentile\n"
                 f"mean ± σ over {tag}; dotted lines = the two operating points "
                 f"({', '.join(str(p) for p in aggregate['operating_points'])})")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    return path


def report(aggregate, paths, args, seeds, tag):
    """Console output is ASCII: this stdout is cp1252 and 'σ' raises there."""
    mapping = aggregate["mapping"]
    print()
    print(f"=== Phase 5 - {args.dataset} d={args.dim}, seeds {seeds} ({tag}), "
          f"mean +/- sigma ===")
    print(f"code: {aggregate['code']}")
    print(f"N (tokens encoded) = {mapping['n_tokens_encoded']}   "
          f"V (mapped types) = {mapping['n_types_mapped']}   "
          f"dropped as unmapped = {mapping['n_tokens_dropped_unmapped']}   "
          f"nodes = {mapping['n_nodes']}/{mapping['subtree_nodes']}")
    for percentile in aggregate["operating_points"]:
        print()
        print(f"-- auto-threshold percentile p = {percentile} "
              f"{'(the prototype default)' if percentile == PERCENTILE else ''}")
        head = (f"{'side':<16}{'rows':>6}{'threshold':>18}{'clusters':>16}"
                f"{'bits/tok':>10}{'size before':>13}{'size after':>20}"
                f"{'ratio':>20}{'ratio (no ceil)':>20}")
        print(head)
        print("-" * len(head))
        for side, entry in aggregate["sides"].items():
            cell = entry["grid"][_pkey(percentile)]
            print(f"{side:<16}{entry['n_rows']:>6}"
                  f"{_clamped(cell['threshold']):>18}"
                  f"{_ascii(cell['n_clusters'], 2):>16}"
                  f"{cell['bits_per_token_after']['mean']:>10.2f}"
                  f"{cell['size_before_bits']['mean']:>13.0f}"
                  f"{_ascii(cell['size_after_bits'], 0):>20}"
                  f"{_ascii(cell['ratio'], 4):>20}"
                  f"{_ascii(cell['ratio_ideal'], 4):>20}")
        head = (f"{'side':<16}{'collapsed tok':>20}{'resid bits/tok':>18}"
                f"{'gold hops':>16}{'hops max':>10}{'largest cluster':>20}")
        print(head)
        print("-" * len(head))
        for side, entry in aggregate["sides"].items():
            cell = entry["grid"][_pkey(percentile)]
            print(f"{side:<16}{_ascii(cell['collapsed_token_fraction'], 4):>20}"
                  f"{_ascii(cell['residual_bits_per_token'], 3):>18}"
                  f"{_ascii(cell['gold_hops_token_weighted'], 2):>16}"
                  f"{cell['gold_hops_max']['mean']:>10.1f}"
                  f"{_ascii(cell['largest_cluster_token_share'], 4):>20}")
    print()
    print(f"gold hops are shortest paths in the frozen hierarchy; its diameter is "
          f"{aggregate['graph_diameter']:.0f} hops")
    print(f"mapping floor, no geometry involved (K = {mapping['n_nodes']} synsets "
          f"for V = {mapping['n_types_mapped']} types): ratio "
          f"{aggregate['ratio_at_no_clustering']:.4f}")
    print(f"the stated code spends {_bits(mapping['n_types_mapped'])} bits/token "
          f"before clustering, against an entropy of "
          f"{mapping['type_entropy_bits']:.3f} bits/token for the same type "
          f"distribution: that gap is the fixed-width code's own slack, and it is "
          f"identical on every side")
    print("distance distribution of each side (why a threshold can hit the "
          "prototype's 1e-6 clamp):")
    for side, entry in aggregate["sides"].items():
        print(f"  {side:<16}median pair distance "
              f"{_ascii(entry['pair_distance_median'], 4)}   zero-distance pairs "
              f"{_ascii(entry['zero_pair_fraction'], 4)}")
    if aggregate.get("js_cap_diagnostic"):
        cap = aggregate["js_cap_diagnostic"]
        print(f"  js-cooccurrence at its own default maxVocab "
              f"{cap['max_vocab']} ({_ascii(cap['types_present'], 1)} of the mapped "
              f"types survive the cap): zero-distance pairs "
              f"{_ascii(cap['zero_pair_fraction'], 4)}")
    print("prototype's own unit-free estimate (K + 0.5V)/N, not comparable to the "
          "ratio above:")
    for side, entry in aggregate["sides"].items():
        values = ", ".join(
            f"p={p}: {entry['grid'][_pkey(p)]['ratio_prototype_units']['mean']:.4f}"
            for p in aggregate["operating_points"])
        print(f"  {side:<16}{values}")
    print()
    for name, path in paths.items():
        print(f"  {name}: {path}")
    print()
    print("regenerate:")
    print(f"  python compress.py --dataset {args.dataset} --dim {args.dim} "
          f"--seeds {args.seeds} --out {args.out}")


def _ascii(stat, digits):
    return f"{stat['mean']:.{digits}f} +/- {stat['sigma']:.{digits}f}"


def _clamped(stat):
    """Flag a threshold sitting on one of the prototype's own clamps.

    `compressionTest.js:531-535` bounds the auto-threshold to [1e-6, 10]. On an
    embedding whose radius is O(10^3) the upper clamp binds, and then the clamp
    rather than the percentile decides the clustering — which has to be visible
    in the table, not deduced from it.
    """
    mean = stat["mean"]
    marker = " (clamp)" if mean >= 10.0 or mean <= 1e-6 else ""
    return f"{mean:.6f}{marker}"


def _pkey(percentile):
    """Grid key. Four decimals: the grid reaches 0.002, and two would collide."""
    return f"{percentile:.4f}"


def _operating_points(args):
    """The two percentiles the tables report: the prototype's default and the
    sparse point fixed from the node count (see PERCENTILE_SPARSE)."""
    return tuple(p for p in (args.percentile, PERCENTILE_SPARSE) if p in args.sweep)


def _write_json(path, payload):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, default=_jsonable)
        fh.write("\n")


def _jsonable(value):
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    raise TypeError(f"{type(value)} is not JSON-serialisable")


# --------------------------------------------------------------------------- #
# Phase 5d (addendum) — the rate-distortion figure, additive and read-only
# --------------------------------------------------------------------------- #

FIGURE_DIMS = (2, 5, 10)
SIDE_COLOURS = {"euclidean": "#1f77b4", "lorentz": "#d62728",
                "js-cooccurrence": "#2ca02c"}
DIM_MARKERS = {2: "o", 5: "s", 10: "^"}
# The stated code's own reference points, both at zero loss: the fixed-width
# cost before any clustering, and the entropy of the same type distribution.
# The second is a floor that measures the first one's slack, not a rival codec
# (CONSTRAINTS.md: no comparison against gzip or any entropy coder).
ISO_COST_LINES = (8.0, 9.0, 10.0)


def main_figure(args):
    """`--figure rate-distortion`: two panels drawn from the existing
    aggregates. Reads out/, writes one PNG into --out, computes no accounting."""
    aggregates = _load_aggregates(args)
    blind_hops, n_nodes = hierarchy_blind_hops(args)
    path = _plot_rate_distortion(aggregates, blind_hops, args)
    print(f"hierarchy-blind gold-hops reference over {n_nodes} clustered "
          f"synsets (all-pairs mean, frozen hierarchy): {blind_hops:.4f}")
    print(f"dimensions plotted: {', '.join(f'd={d}' for d in sorted(aggregates))}"
          f"   cells: {sum(len(SIDES) * len(a['percentile_grid']) for a in aggregates.values())}")
    print(f"wrote {path}")
    return 0


def _load_aggregates(args):
    """The Phase-5 / Phase-5b aggregates, read as they are. A missing dimension
    names the command that produces it rather than being silently skipped."""
    tag = ablation.seed_tag(args.seed, args.seeds)
    found = {}
    for dim in FIGURE_DIMS:
        path = os.path.join(args.aggregate_dir,
                            f"compress_{args.dataset}_d{dim}_{tag}.json")
        if not os.path.exists(path):
            raise SystemExit(
                f"missing aggregate {path}; regenerate it with\n"
                f"  python compress.py --dataset {args.dataset} --dim {dim} "
                f"--seeds {args.seeds} --out {args.aggregate_dir}/")
        with open(path, encoding="utf-8") as fh:
            found[dim] = json.load(fh)
    return found


def hierarchy_blind_hops(args):
    """What a clustering that ignores the hierarchy scores: the all-pairs mean
    shortest path over the clustered synsets, in the frozen hierarchy. Published
    as 7.654 in the Phase-5 record; re-derived here rather than transcribed."""
    path = os.path.join(args.aggregate_dir,
                        f"compress_mapping_pg{CORPUS_ID}_{args.dataset}.json")
    if not os.path.exists(path):
        raise SystemExit(f"missing mapping artifact {path}")
    with open(path, encoding="utf-8") as fh:
        nodes = sorted(json.load(fh)["node_index"])
    hierarchy = datasets.load(args.dataset, seed=args.seed)
    block = np.asarray(hierarchy.graph_dist, dtype=np.float64)[np.ix_(nodes, nodes)]
    upper = np.triu_indices(len(nodes), 1)
    return float(block[upper].mean()), len(nodes)


def _plot_rate_distortion(aggregates, blind_hops, args):
    """Left: code length against the loss it buys, with the iso-cost diagonals.
    Right: code length against the semantic damage, with the hierarchy-blind
    reference. One point per (side, percentile, dimension) cell, mean over the
    seed set — never a single seed (CLAUDE.md)."""
    tag = ablation.seed_tag(args.seed, args.seeds)
    dims = sorted(aggregates)
    path = os.path.join(args.out, f"rate_distortion_{args.dataset}"
                                  f"_d{'-'.join(str(d) for d in dims)}_{tag}.png")
    fig, (left, right) = plt.subplots(1, 2, figsize=(13.5, 5.4))

    for total in ISO_COST_LINES:
        left.plot([0.0, total], [total, 0.0], color="grey", linestyle="--",
                  linewidth=0.9, zorder=1)
        left.annotate(f"code + loss = {total:.0f}", xy=(total - 0.35, 0.42),
                      rotation=-38, fontsize=7.5, color="grey", ha="right")

    for dim in dims:
        aggregate = aggregates[dim]
        grid = aggregate["percentile_grid"]
        for side, entry in aggregate["sides"].items():
            cells = [entry["grid"][_pkey(p)] for p in grid]
            code = [c["bits_per_token_after"]["mean"] for c in cells]
            loss = [c["residual_bits_per_token"]["mean"] for c in cells]
            hops = [c["gold_hops_token_weighted"]["mean"] for c in cells]
            style = dict(color=SIDE_COLOURS[side], marker=DIM_MARKERS[dim],
                         markersize=5.5, linestyle="none", alpha=0.85, zorder=3,
                         label=f"{side}, d={dim}")
            left.plot(code, loss, **style)
            right.plot(code, hops, **style)

    mapping = aggregates[dims[0]]["mapping"]
    before = float(_bits(mapping["n_types_mapped"]))
    entropy = float(mapping["type_entropy_bits"])
    left.plot([before], [0.0], marker="*", markersize=15, color="black", zorder=4,
              linestyle="none",
              label=f"stated code before clustering ({before:.2f}, 0)")
    left.plot([entropy], [0.0], marker="P", markersize=10, color="dimgrey",
              zorder=4, linestyle="none",
              label=f"type-entropy floor ({entropy:.3f}, 0)")
    left.set_xlabel("code length, bits/token  ⌈log2 K⌉")
    left.set_ylabel("residual loss, bits/token  H(type | cluster)")
    left.set_title("Every cell sits on the same iso-cost diagonal:\n"
                   "bits leave the code and reappear in the loss\n"
                   "(cells coincide wherever ⌈log2 K⌉ agrees)", fontsize=10)
    left.set_xlim(left=0.0)
    left.set_ylim(bottom=-0.25)
    left.legend(fontsize=6.5, loc="upper right", ncol=2)

    right.axhline(blind_hops, color="black", linestyle="-.", linewidth=1.1,
                  zorder=2)
    right.annotate(f"hierarchy-blind reference = {blind_hops:.3f} hops",
                   xy=(0.02, blind_hops + 0.12), xycoords=("axes fraction", "data"),
                   fontsize=7.5)
    right.set_xlabel("code length, bits/token  ⌈log2 K⌉")
    right.set_ylabel("semantic damage, token-weighted gold hops")
    right.set_title("The shorter the code, the further the merges travel\n"
                    "in the gold hierarchy")
    right.set_xlim(left=0.0)
    right.set_ylim(bottom=-0.3)

    fig.suptitle(f"{args.dataset} — semantic quantization on the rate-distortion "
                 f"plane; {tag}, mean over the seed set\n"
                 f"colour = side, marker = dimension; "
                 f"every value read from out/compress_{args.dataset}_d*_{tag}.json")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def _parse_args(argv):
    p = argparse.ArgumentParser(
        description="Phase 5: the prototype's semantic-compression accounting, "
                    "run on the learned Euclidean and Lorentz embeddings.")
    p.add_argument("--dataset", default="wordnet-mammals", choices=datasets.DATASETS)
    p.add_argument("--dim", type=int, default=2)
    p.add_argument("--dims", type=int, nargs="+", default=None,
                   help="Phase 5b (addendum): run the pipeline at several "
                        "dimensions in one command instead of --dim's one. "
                        "Additive -- reuses every function --dim uses "
                        "unmodified; see the PHASE 5b docstring section for "
                        "what it does and does not recompute.")
    p.add_argument("--seeds", type=int, default=5,
                   help="how many seeds: base, base+1, ..., base+seeds-1")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED,
                   help="base seed of the seed set")
    p.add_argument("--out", default="out")
    p.add_argument("--percentile", type=float, default=PERCENTILE,
                   help="the prototype's autoThresholdPercentile (default 0.35); "
                        f"the tables also report p={PERCENTILE_SPARSE}, see "
                        f"PERCENTILE_SPARSE")
    p.add_argument("--sweep", type=float, nargs="+", default=list(SWEEP),
                   help="percentile grid for the sensitivity figure; both "
                        "operating points are added to it if absent")
    p.add_argument("--max-vocab", type=int, default=0,
                   help="the prototype's maxVocab; 0 = no cap. The cap exists to "
                        "bound its O(V^2) clustering, which does not bind here, "
                        "and at the JS default 5000 it removes 49%% of the mapped "
                        "types (259 -> 133) and 42%% of the nodes (166 -> 96), "
                        "because mammal names are rare words")
    p.add_argument("--corpus-file", default=None,
                   help="use this text instead of fetching PG #2300 (offline reruns)")
    p.add_argument("--no-js", action="store_true",
                   help="skip the JS co-occurrence baseline (needs node on PATH)")
    p.add_argument("--figure", choices=("rate-distortion",), default=None,
                   help="Phase 5d (addendum): draw a figure from the aggregates "
                        "already in --aggregate-dir and exit. Measures nothing "
                        "and writes nothing but the PNG, into --out.")
    p.add_argument("--aggregate-dir", default="out",
                   help="where --figure reads the existing aggregates from "
                        "(default out/); --out is where the figure is written")
    args = p.parse_args(argv)
    args.sweep = sorted(set(args.sweep) | {args.percentile, PERCENTILE_SPARSE})
    return args


if __name__ == "__main__":
    sys.exit(main())
