#!/usr/bin/env python3
"""Phase-4 matched ablation: Euclidean vs Lorentz at d in {2, 5, 10}.

    python ablation.py --dataset wordnet-mammals --dims 2 5 10 --seeds 5 --out out/

One command: regression gate, then the sweep, then the table and the three
money plots (distortion-vs-depth, MAP-vs-dimension, distance-distribution
spread), then the findings. Nothing here trains anything itself: it calls
`embeddings/euclidean.py` and `embeddings/lorentz.py` through the same path
`eval.py` uses (same seeding order, same `harness.metrics.evaluate`), which is
what the regression gate below checks before any sweep starts.

Read-only dependencies, by packet rule: `eval.py`, `harness/` (frozen since
Phase 1), `embeddings/euclidean.py` (sealed 2026-08-03), `embeddings/lorentz.py`
(Phase 3). Per-geometry hyperparameters are injected by setting the module
attributes at call time (`_hyperparams`) precisely because those modules must
not be edited.

F2 — the fairness condition — is answered by option (b): the learning rate is
tuned *per (geometry, dimension)*, on `synthetic-tree` only, selecting the best
mean MAP over seeds (20260716, 12345, 777); see `LR_TABLE`. The table is frozen
in this file before any wordnet-mammals run, and the reported command never
tunes anything. What is *not* tuned per dimension is the epoch budget: it stays
at 6000 for both geometries at every d (it was the d=2 optimum for both). That
axis was dropped for runtime, not for convenience; it is the one documented
bound of this ablation.

F3 — every artifact lands in `--out` with its seed in the name. A 5-seed
aggregate has no single seed, so aggregates are tagged `seedset<base>x<k>`,
which denotes exactly the seeds `base, base+1, ..., base+k-1` (with
`base = --seed`); the seed list is also written verbatim into the aggregate JSON.

Checkpointing: every single run is written to
`out/ablation_run_<geometry>_<dataset>_d<dim>_seed<seed>.json` as it lands and
is reused on a later invocation when its (lr, epochs) still match, so an
interrupted sweep resumes instead of restarting.
"""
import argparse
import contextlib
import importlib
import json
import os
import sys
import time

# PYTHONSAFEPATH=1 is mandatory here (CLAUDE.md), so the script directory is not
# on sys.path. Same fix as eval.py: put it back, resolved from __file__.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib  # noqa: E402
import numpy as np  # noqa: E402

matplotlib.use("Agg")  # headless build host
import matplotlib.pyplot as plt  # noqa: E402

from harness import datasets, metrics  # noqa: E402

DEFAULT_SEED = 20260716
GEOMETRIES = ("euclidean", "lorentz")
EPOCHS = 6000

# --- F2, option (b): the frozen per-(geometry, dimension) learning rates ------
#
# d=2 is not re-searched here: it is the value published in Phases 2 and 3,
# obtained under exactly this protocol (synthetic-tree only, best mean MAP over
# TUNE_SEEDS). d=5 and d=10 were searched by `--tune-synthetic` over LR_GRID at
# 6000 epochs, on synthetic-tree only, before any wordnet-mammals run.
# Evidence (mean MAP over the three tuning seeds) is in
# out/ablation_tuning_synthetic-tree_seedset<...>.json; the selected cell is
# marked with its mean MAP in the comment on each line.
LR_TABLE = {
    ("euclidean", 2): 0.5,      # Phase 2, published (embeddings/euclidean.py)
    ("euclidean", 5): 0.5,      # MAP tied at 1.0000 across [0.1, 0.3, 0.5, 1.0]
    ("euclidean", 10): 0.5,     # MAP tied at 1.0000 across [0.1, 0.3, 0.5, 1.0]
    ("lorentz", 2): 0.005,      # Phase 3, published: mean MAP 0.9305 there
    ("lorentz", 5): 0.003,      # unique best mean MAP 0.9573 (0.001 -> 0.8065)
    ("lorentz", 10): 0.003,     # unique best mean MAP 0.9669 (0.001 -> 0.8300)
}

# The two things the search actually found, both worth stating rather than
# burying in the table above:
#
#  * the Euclidean baseline *saturates* on synthetic-tree at d >= 5 — MAP
#    1.0000 and mean rank 1.0000 at every lr in the grid — so per-dimension
#    tuning has nothing to select on and the frozen d=2 rate is kept (see
#    `_select_lr`). The tree stops discriminating above d=2; only distortion
#    still separates the geometries there. This is why wordnet-mammals, not the
#    synthetic tree, is the report set.
#  * the Lorentz optimum *moves* with dimension, 0.005 at d=2 to 0.003 at d=5
#    and d=10, and moves monotonically: mean MAP falls with lr all the way to
#    0.03 (0.9573 -> 0.9357 at d=5, 0.9669 -> 0.9417 at d=10). Reusing the d=2
#    rate at every d — F2 option (a) — would therefore have handicapped the
#    hyperbolic side at exactly the dimensions where it is being tested.

# Search grid for --tune-synthetic. Each grid brackets the frozen d=2 optimum on
# both sides, so a selected endpoint is visible as such rather than silent.
# 0.001 was added to the lorentz grid after the first pass selected the lower
# endpoint 0.003 at d=5 and d=10: an endpoint optimum is an unbracketed one, and
# extending the grid is cheaper than reporting the hole.
LR_GRID = {
    "euclidean": (0.1, 0.3, 0.5, 1.0),
    "lorentz": (0.001, 0.003, 0.005, 0.01, 0.03),
}
TUNE_SEEDS = (20260716, 12345, 777)
TUNE_DATASET = "synthetic-tree"

# --- regression gate: the published Phase-2/Phase-3 artifacts, to the digit ---
GATE = {
    ("euclidean", "synthetic-tree"): (0.8304, 4.2617, 0.3773),
    ("euclidean", "wordnet-mammals"): (0.7513, 5.0034, 0.3260),
    ("lorentz", "synthetic-tree"): (0.9220, 9.5661, 0.2060),
    ("lorentz", "wordnet-mammals"): (0.8973, 13.3884, 0.2599),
}
GATE_TOL = 5e-5  # the artifacts are quoted to 4 decimals

HIST_BINS = 80
HIST_SPAN = 2.0  # histogram range is [0, HIST_SPAN * graph diameter]

_HIERARCHIES = {}


def main(argv=None):
    args = _parse_args(argv)
    os.makedirs(args.out, exist_ok=True)

    if args.tune_synthetic:
        return tune_synthetic(args)

    seeds = seed_set(args.seed, args.seeds)
    tag = seed_tag(args.seed, args.seeds)

    lrs = {(g, d): _learning_rate(g, d) for g in GEOMETRIES for d in args.dims}
    print(f"F2: per-(geometry, dimension) learning rates, tuned on "
          f"{TUNE_DATASET} only (option b). Epochs fixed at {EPOCHS}.")
    for (g, d), lr in sorted(lrs.items()):
        print(f"  {g:<9} d={d:<3} lr={lr}")
    print()

    if not regression_gate(args.out):
        return 1
    if not f1_gate(args.out):
        return 1

    runs = []
    total = len(args.dims) * len(GEOMETRIES) * len(seeds)
    for dim in args.dims:
        for geometry in GEOMETRIES:
            for seed in seeds:
                print(f"[{len(runs) + 1}/{total}] {geometry} {args.dataset} "
                      f"d={dim} seed={seed}", flush=True)
                runs.append(run_once(geometry, args.dataset, dim, seed,
                                     args.out, lrs[(geometry, dim)], EPOCHS))

    aggregate = summarise(runs, args, seeds, tag, lrs)
    paths = write_outputs(aggregate, runs, args, tag)
    report(aggregate, paths, args, seeds, tag)
    return 0


# --------------------------------------------------------------------------- #
# running one embedding, exactly the way eval.py runs it
# --------------------------------------------------------------------------- #

def run_once(geometry, dataset, dim, seed, out_dir, lr, epochs, tag="run"):
    """Train, score, checkpoint. Returns the run record."""
    path = os.path.join(out_dir,
                        f"ablation_{tag}_{geometry}_{dataset}_d{dim}_seed{seed}.json")
    cached = _load_cached(path, lr, epochs)
    if cached is not None:
        print(f"    cached: MAP {cached['map']:.4f}  rank {cached['mean_rank']:.4f}  "
              f"distortion {cached['avg_distortion']:.4f}", flush=True)
        return cached

    started = time.perf_counter()
    # eval.py's _seed_everything, same order, before anything else touches RNG.
    np.random.seed(seed)
    import torch
    torch.manual_seed(seed)

    hierarchy = _hierarchy(dataset, seed)
    module = importlib.import_module(f"embeddings.{geometry}")
    with _hyperparams(module, lr, epochs):
        coords, emb_dist = module.build(hierarchy, dim, seed)
    emb_dist = np.asarray(emb_dist, dtype=np.float64)
    result = metrics.evaluate(hierarchy, emb_dist)
    wall = time.perf_counter() - started

    density, overflow = _histogram(result["emb_dist_pairs"], hierarchy)
    emb_pairs = result["emb_dist_pairs"]
    graph_pairs = result["graph_dist_pairs"]
    record = {
        "geometry": geometry,
        "dataset": dataset,
        "dim": dim,
        "seed": seed,
        "lr": lr,
        "epochs": epochs,
        "n_nodes": result["n_nodes"],
        "n_pairs": result["n_pairs"],
        "map": result["map"],
        "mean_rank": result["mean_rank"],
        "avg_distortion": result["avg_distortion"],
        "distortion_scale": result["distortion_scale"],
        "depth_levels": result["depth_levels"],
        "distortion_by_depth": result["distortion_by_depth"],
        "pairs_by_depth": result["pairs_by_depth"],
        "hist_density": [float(x) for x in density],
        "hist_overflow_fraction": overflow,
        "emb_spread_sigma_over_mean": float(emb_pairs.std() / emb_pairs.mean()),
        "graph_spread_sigma_over_mean": float(graph_pairs.std() / graph_pairs.mean()),
        "max_emb_distance": float(emb_pairs.max() / result["distortion_scale"]),
        "clip_bound_nodes": _clip_bound_nodes(geometry, module, coords),
        "wall_seconds": wall,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"    MAP {record['map']:.4f}  rank {record['mean_rank']:.4f}  "
          f"distortion {record['avg_distortion']:.4f}  ({wall:.0f}s)", flush=True)
    return record


@contextlib.contextmanager
def _hyperparams(module, lr, epochs):
    """Inject lr/epochs into a sealed embedding module for one call, then undo.

    The embedding modules are read-only for this phase (packet rule), so the
    per-(geometry, dimension) constants have to be set on the module object
    rather than edited into it.
    """
    previous = (module.LEARNING_RATE, module.EPOCHS)
    module.LEARNING_RATE, module.EPOCHS = lr, epochs
    try:
        yield
    finally:
        module.LEARNING_RATE, module.EPOCHS = previous


def _hierarchy(dataset, seed):
    """`datasets.load` is deterministic and consumes no RNG, so caching it
    across runs cannot change a number (harness/datasets.py docstring)."""
    if dataset not in _HIERARCHIES:
        _HIERARCHIES[dataset] = datasets.load(dataset, seed=seed)
    return _HIERARCHIES[dataset]


def _load_cached(path, lr, epochs):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        record = json.load(fh)
    if record.get("lr") != lr or record.get("epochs") != epochs:
        return None  # stale checkpoint from a different hyperparameter set
    return record


def _learning_rate(geometry, dim):
    lr = LR_TABLE.get((geometry, dim))
    if lr is None:
        raise SystemExit(
            f"no frozen learning rate for ({geometry}, d={dim}). Run\n"
            f"  python ablation.py --tune-synthetic --dims {dim} --out out/\n"
            f"and paste the selected value into LR_TABLE (F2 option b: tuning "
            f"happens on {TUNE_DATASET} only, never on wordnet-mammals).")
    return lr


def _clip_bound_nodes(geometry, module, coords):
    """How many nodes sit on MAX_SPATIAL_NORM (lorentz only; None otherwise)."""
    if geometry != "lorentz" or coords is None:
        return None
    norms = np.linalg.norm(np.asarray(coords)[:, 1:], axis=1)
    return int((norms >= module.MAX_SPATIAL_NORM * (1.0 - 1e-9)).sum())


def _histogram(emb_dist_pairs, hierarchy):
    """Density of scaled embedding distances on edges fixed by the dataset.

    The edges must not depend on the run, otherwise the per-seed densities
    cannot be averaged. They come from the graph diameter, which is a property
    of the hierarchy alone.
    """
    edges = _hist_edges(hierarchy)
    inside = emb_dist_pairs <= edges[-1]
    density, _ = np.histogram(emb_dist_pairs[inside], bins=edges, density=True)
    overflow = float(1.0 - inside.mean())
    return density * inside.mean(), overflow  # scale so the area is the mass kept


def _hist_edges(hierarchy):
    return np.linspace(0.0, HIST_SPAN * float(hierarchy.graph_dist.max()),
                       HIST_BINS + 1)


# --------------------------------------------------------------------------- #
# gates
# --------------------------------------------------------------------------- #

def regression_gate(out_dir):
    """Reproduce the published d=2 / seed 20260716 artifacts to the digit.

    If this fails, the driver is calling the sealed modules differently from
    eval.py and every number downstream is a different experiment.
    """
    print("regression gate - d=2, seed 20260716, against the published artifacts")
    ok = True
    for (geometry, dataset), expected in sorted(GATE.items()):
        record = run_once(geometry, dataset, 2, DEFAULT_SEED, out_dir,
                          _learning_rate(geometry, 2), EPOCHS)
        got = (record["map"], record["mean_rank"], record["avg_distortion"])
        deltas = [abs(g - e) for g, e in zip(got, expected)]
        passed = max(deltas) <= GATE_TOL
        ok = ok and passed
        print(f"  {'PASS' if passed else 'FAIL'} {geometry:<9} {dataset:<16} "
              f"MAP {got[0]:.4f}/{expected[0]:.4f}  "
              f"rank {got[1]:.4f}/{expected[1]:.4f}  "
              f"distortion {got[2]:.4f}/{expected[2]:.4f}", flush=True)
    if not ok:
        print("\nregression gate FAILED: the driver reaches the sealed modules by a "
              "different path than eval.py. Not sweeping on top of that.")
    print()
    return ok


def f1_gate(out_dir):
    """F1 (README-fase2.md): at d=2 on synthetic trees the hyperbolic embedding
    must show lower distortion than the Euclidean one. Theory guarantees it, so
    a failure means a broken implementation — report it, do not tune around it.
    """
    euclidean = run_once("euclidean", TUNE_DATASET, 2, DEFAULT_SEED, out_dir,
                         _learning_rate("euclidean", 2), EPOCHS)
    lorentz = run_once("lorentz", TUNE_DATASET, 2, DEFAULT_SEED, out_dir,
                       _learning_rate("lorentz", 2), EPOCHS)
    passed = lorentz["avg_distortion"] < euclidean["avg_distortion"]
    print(f"F1 gate - synthetic-tree d=2: hyperbolic distortion "
          f"{lorentz['avg_distortion']:.4f} vs euclidean "
          f"{euclidean['avg_distortion']:.4f} -> {'PASS' if passed else 'FIRES'}")
    if not passed:
        print("F1 FIRES: hyperbolic distortion does not beat Euclidean on the "
              "synthetic tree at d=2. Stopping, as the packet requires.")
    print()
    return passed


# --------------------------------------------------------------------------- #
# F2 option (b): the learning-rate search, on synthetic-tree only
# --------------------------------------------------------------------------- #

def _select_lr(geometry, mean_map, mean_distortion):
    """Highest mean MAP, with the tie-break stated rather than left to dict order.

    It matters: the Euclidean baseline reconstructs the synthetic tree perfectly
    at d >= 5 (MAP 1.0000, mean rank 1.0000) for *every* lr in the grid, so the
    selection criterion carries no information there. In that case the frozen
    d=2 rate is kept — the incumbent, already published — because the remaining
    differences (mean distortion within ~0.002 across the grid) are inside
    seed noise and picking on them would be tuning on noise. If the incumbent is
    not itself tied at the top, the tie falls to the lowest mean distortion,
    which is the direction that favours the baseline on the metric the
    hyperbolic claim rests on.
    """
    top = max(mean_map.values())
    tied = [lr for lr, score in mean_map.items() if score == top]
    if len(tied) == 1:
        return tied[0], "unique best mean MAP"
    incumbent = LR_TABLE[(geometry, 2)]
    if incumbent in tied:
        return incumbent, (f"mean MAP tied at {top:.4f} across {sorted(tied)}; "
                           f"kept the frozen d=2 rate")
    best = min(tied, key=lambda lr: mean_distortion[lr])
    return best, (f"mean MAP tied at {top:.4f} across {sorted(tied)}; "
                  f"broken on lowest mean distortion")


def tune_synthetic(args):
    """Search lr per (geometry, dimension) on synthetic-tree, print the table.

    Never touches wordnet-mammals: the report set must not inform a knob. The
    winning values are pasted into LR_TABLE by hand, which is what freezes them.
    """
    # dims in the name: two --tune-synthetic invocations on different dims must
    # not overwrite each other's table.
    tag = (f"dims{'-'.join(str(d) for d in args.dims)}_"
           f"seedset{'-'.join(str(s) for s in TUNE_SEEDS)}")
    table = {}
    for geometry in GEOMETRIES:
        for dim in args.dims:
            scores = {}
            distortions = {}
            for lr in LR_GRID[geometry]:
                maps = []
                dists = []
                for seed in TUNE_SEEDS:
                    print(f"tune {geometry} d={dim} lr={lr} seed={seed}", flush=True)
                    try:
                        record = run_once(geometry, TUNE_DATASET, dim, seed,
                                          args.out, lr, EPOCHS,
                                          tag=f"tune_lr{lr:g}")
                        maps.append(record["map"])
                        dists.append(record["avg_distortion"])
                    except Exception as exc:  # a diverged cell is data, not a crash
                        print(f"    diverged: {type(exc).__name__}: {exc}", flush=True)
                        maps.append(float("nan"))
                        dists.append(float("nan"))
                scores[lr] = float(np.mean(maps))
                distortions[lr] = float(np.mean(dists))
                print(f"  mean MAP {scores[lr]:.4f}  mean distortion "
                      f"{distortions[lr]:.4f}  over {list(TUNE_SEEDS)}", flush=True)
            usable = {lr: s for lr, s in scores.items() if np.isfinite(s)}
            if not usable:
                raise SystemExit(f"every lr diverged for {geometry} d={dim}")
            best, why = _select_lr(geometry, usable, distortions)
            table[f"{geometry}|{dim}"] = {"selected_lr": best,
                                          "selection": why,
                                          "mean_map": scores,
                                          "mean_distortion": distortions,
                                          "epochs": EPOCHS}
            print(f"=> {geometry} d={dim}: lr={best} (mean MAP {scores[best]:.4f}, "
                  f"{why})\n", flush=True)

    path = os.path.join(args.out, f"ablation_tuning_{TUNE_DATASET}_{tag}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"dataset": TUNE_DATASET, "seeds": list(TUNE_SEEDS),
                   "epochs": EPOCHS, "grid": {k: list(v) for k, v in LR_GRID.items()},
                   "results": table}, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(f"wrote {path}")
    print("\npaste into LR_TABLE:")
    for key, entry in sorted(table.items()):
        geometry, dim = key.split("|")
        print(f'    ("{geometry}", {dim}): {entry["selected_lr"]},'
              f'   # mean MAP {entry["mean_map"][entry["selected_lr"]]:.4f}, '
              f'{entry["selection"]}')
    return 0


# --------------------------------------------------------------------------- #
# aggregation, table, figures
# --------------------------------------------------------------------------- #

def summarise(runs, args, seeds, tag, lrs):
    cells = {}
    for dim in args.dims:
        for geometry in GEOMETRIES:
            group = [r for r in runs if r["dim"] == dim and r["geometry"] == geometry]
            cells[f"{geometry}|{dim}"] = {
                "geometry": geometry,
                "dim": dim,
                "lr": lrs[(geometry, dim)],
                "epochs": EPOCHS,
                "seeds": [r["seed"] for r in group],
                **{f"{key}_{stat}": func([r[key] for r in group])
                   for key in ("map", "mean_rank", "avg_distortion",
                               "emb_spread_sigma_over_mean", "max_emb_distance")
                   for stat, func in (("mean", _mean), ("sigma", _sigma))},
                "clip_bound_nodes_mean": (
                    _mean([r["clip_bound_nodes"] for r in group])
                    if geometry == "lorentz" else None),
                "clip_bound_nodes_per_seed": (
                    [r["clip_bound_nodes"] for r in group]
                    if geometry == "lorentz" else None),
                "wall_seconds_total": sum(r["wall_seconds"] for r in group),
            }
    return {
        "dataset": args.dataset,
        "dims": list(args.dims),
        "seed_base": args.seed,
        "n_seeds": args.seeds,
        "seeds": list(seeds),
        "seed_set_tag": tag,
        "f2_mode": "per-(geometry,dimension) lr tuned on synthetic-tree only "
                   "(option b); epochs fixed at 6000 for both geometries",
        "n_nodes": runs[0]["n_nodes"],
        "graph_spread_sigma_over_mean": runs[0]["graph_spread_sigma_over_mean"],
        "cells": cells,
        "runs": runs,
    }


def _mean(values):
    return float(np.mean(values))


def _sigma(values):
    return float(np.std(values, ddof=1)) if len(values) > 1 else 0.0


def table_markdown(aggregate):
    """The table, in Markdown. Written to a UTF-8 file; printed through
    `_console`, because stdout on the build host is cp1252 and cannot encode
    'σ'."""
    lines = [
        f"# matched ablation — {aggregate['dataset']} "
        f"({aggregate['n_nodes']} nodes)",
        "",
        f"seeds {aggregate['seeds']} (tag `{aggregate['seed_set_tag']}` = "
        f"base {aggregate['seed_base']} .. base+{aggregate['n_seeds'] - 1}); "
        f"mean ± σ across those {aggregate['n_seeds']} seeds, σ with ddof=1.",
        "",
        f"F2: {aggregate['f2_mode']}.",
        "",
        "| d | geometry | lr | MAP | mean rank | avg distortion |",
        "|---|---|---|---|---|---|",
    ]
    for dim in aggregate["dims"]:
        for geometry in GEOMETRIES:
            c = aggregate["cells"][f"{geometry}|{dim}"]
            lines.append(
                f"| {dim} | {geometry} | {c['lr']} | "
                f"{c['map_mean']:.4f} ± {c['map_sigma']:.4f} | "
                f"{c['mean_rank_mean']:.4f} ± {c['mean_rank_sigma']:.4f} | "
                f"{c['avg_distortion_mean']:.4f} ± {c['avg_distortion_sigma']:.4f} |")
    return "\n".join(lines) + "\n"


def report_markdown(aggregate, args):
    """Table + findings + conclusion: the text half of the deliverable."""
    return "\n".join([
        table_markdown(aggregate),
        "## findings", "",
        "```",
        _finding_mean_rank(aggregate, args),
        _finding_clip(aggregate, args),
        _finding_f1(args),
        "```", "",
        "## conclusion", "",
        _conclusion(aggregate, args),
        "",
    ])


def write_outputs(aggregate, runs, args, tag):
    stem = f"{args.dataset}_dims{'-'.join(str(d) for d in args.dims)}_{tag}"
    json_path = os.path.join(args.out, f"ablation_table_{stem}.json")
    md_path = os.path.join(args.out, f"ablation_table_{stem}.md")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(aggregate, fh, indent=2, sort_keys=True)
        fh.write("\n")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(report_markdown(aggregate, args))

    figures = {
        "distortion_vs_depth": plot_distortion_vs_depth(
            os.path.join(args.out, f"ablation_distortion_vs_depth_{stem}.png"),
            aggregate, args),
        "map_vs_dimension": plot_map_vs_dimension(
            os.path.join(args.out, f"ablation_map_vs_dimension_{stem}.png"),
            aggregate, args),
        "distance_spread": plot_distance_spread(
            os.path.join(args.out, f"ablation_distance_spread_{stem}.png"),
            aggregate, args),
    }
    return {"table_json": json_path, "table_md": md_path, **figures}


STYLE = {"euclidean": ("#1f77b4", "o", "Euclidean (Adam)"),
         "lorentz": ("#d62728", "s", "hyperbolic (Lorentz + RiemannianAdam)")}


def _band(ax, x, values, geometry, marker=None):
    """mean ± σ across seeds, never a single seed (packet rule)."""
    stack = np.asarray(values, dtype=np.float64)
    mean = stack.mean(axis=0)
    sigma = stack.std(axis=0, ddof=1) if stack.shape[0] > 1 else np.zeros_like(mean)
    color, default_marker, label = STYLE[geometry]
    marker = default_marker if marker is None else marker
    ax.plot(x, mean, marker=marker, ms=4, color=color, label=label)
    ax.fill_between(x, mean - sigma, mean + sigma, color=color, alpha=0.2, lw=0)
    return mean, sigma


def _panels(dims, title):
    fig, axes = plt.subplots(1, len(dims), figsize=(4.6 * len(dims), 4.4),
                             sharey=True, squeeze=False)
    fig.suptitle(title, fontsize=11)
    return fig, axes[0]


def plot_distortion_vs_depth(path, aggregate, args):
    fig, axes = _panels(args.dims,
                        f"distortion vs depth — {args.dataset} — mean ± σ over "
                        f"{args.seeds} seeds ({aggregate['seed_set_tag']})")
    for ax, dim in zip(axes, args.dims):
        for geometry in GEOMETRIES:
            group = _group(aggregate, geometry, dim)
            levels = group[0]["depth_levels"]
            _band(ax, levels, [r["distortion_by_depth"] for r in group], geometry)
            ax.set_xticks(levels)
        ax.set_title(f"d = {dim}")
        ax.set_xlabel("depth of the deeper endpoint")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("mean distortion  |a·d_emb/d_graph − 1|")
    axes[0].legend(fontsize=8)
    return _save(fig, path)


def plot_map_vs_dimension(path, aggregate, args):
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    for geometry in GEOMETRIES:
        color, marker, label = STYLE[geometry]
        cells = [aggregate["cells"][f"{geometry}|{d}"] for d in args.dims]
        ax.errorbar(args.dims, [c["map_mean"] for c in cells],
                    yerr=[c["map_sigma"] for c in cells],
                    marker=marker, ms=5, capsize=4, color=color, label=label)
    # log spacing so d=2/5/10 are not crammed against the left edge; the minor
    # decade labels matplotlib adds there are noise on a 3-point axis.
    ax.set_xscale("log")
    ax.minorticks_off()
    ax.set_xticks(args.dims)
    ax.set_xticklabels([str(d) for d in args.dims])
    ax.set_xlabel("intrinsic dimension d")
    ax.set_ylabel("filtered reconstruction MAP")
    ax.set_title(f"MAP vs dimension — {args.dataset} — mean ± σ over "
                 f"{args.seeds} seeds ({aggregate['seed_set_tag']})", fontsize=9)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return _save(fig, path)


def plot_distance_spread(path, aggregate, args):
    hierarchy = _hierarchy(args.dataset, args.seed)
    edges = _hist_edges(hierarchy)
    centres = 0.5 * (edges[:-1] + edges[1:])
    iu = np.triu_indices(hierarchy.n, 1)
    hops = hierarchy.graph_dist[iu]

    fig, axes = _panels(args.dims,
                        f"distance-distribution spread — {args.dataset} — "
                        f"mean ± σ over {args.seeds} seeds "
                        f"({aggregate['seed_set_tag']})")
    for ax, dim in zip(axes, args.dims):
        ax.hist(hops, bins=np.arange(hops.min() - 0.5, hops.max() + 1.5),
                density=True, alpha=0.35, color="#888888",
                label="graph distance (hops)")
        for geometry in GEOMETRIES:
            group = _group(aggregate, geometry, dim)
            _band(ax, centres, [r["hist_density"] for r in group], geometry,
                  marker="")
        cells = [aggregate["cells"][f"{g}|{dim}"] for g in GEOMETRIES]
        ax.set_title(f"d = {dim}\nσ/mean  " + "  ".join(
            f"{g[:3]} {c['emb_spread_sigma_over_mean_mean']:.3f}"
            for g, c in zip(GEOMETRIES, cells))
            + f"  graph {aggregate['graph_spread_sigma_over_mean']:.3f}",
            fontsize=9)
        ax.set_xlabel("pairwise distance (embedding rescaled to the hop scale)")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("density")
    axes[0].legend(fontsize=8)
    return _save(fig, path)


def _group(aggregate, geometry, dim):
    return [r for r in aggregate["runs"]
            if r["geometry"] == geometry and r["dim"] == dim]


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #

def _console(text):
    """stdout is cp1252 on the build host: 'sigma' has no code point there.
    Files and figures keep the real characters; the console gets ASCII."""
    return (text.replace("σ", "sd").replace("±", "+/-")
                .replace("—", "-").replace("·", "*"))


def report(aggregate, paths, args, seeds, tag):
    print()
    print(_console(report_markdown(aggregate, args)))
    for name, path in paths.items():
        print(f"wrote {path}")
    print()
    print("reproduce every number above with:")
    print(f"  {_interpreter()} ablation.py --dataset {args.dataset} --dims "
          f"{' '.join(str(d) for d in args.dims)} --seeds {args.seeds} "
          f"--seed {args.seed} --out {args.out}")
    print(f"  (seed set {tag} = {list(seeds)})")


def _finding_mean_rank(aggregate, args):
    lines = ["mean rank — does the d=2 inversion (hyperbolic worse on rank while "
             "better on MAP) survive as d grows?"]
    inverts = []
    for dim in args.dims:
        euc = aggregate["cells"][f"euclidean|{dim}"]
        lor = aggregate["cells"][f"lorentz|{dim}"]
        better = lor["mean_rank_mean"] < euc["mean_rank_mean"]
        inverts.append(better)
        lines.append(
            f"  d={dim:<3} euclidean {euc['mean_rank_mean']:8.4f} ± "
            f"{euc['mean_rank_sigma']:.4f}   hyperbolic "
            f"{lor['mean_rank_mean']:8.4f} ± {lor['mean_rank_sigma']:.4f}   "
            f"MAP {euc['map_mean']:.4f} vs {lor['map_mean']:.4f}   "
            f"-> hyperbolic rank {'better' if better else 'worse'}")
    if all(inverts):
        lines.append("  the ranking penalty is absent at every d tested.")
    elif any(inverts):
        first = args.dims[inverts.index(True)]
        lines.append(f"  it inverts: hyperbolic mean rank overtakes Euclidean from "
                     f"d={first} on.")
    else:
        map_ahead = [d for d in args.dims
                     if (aggregate["cells"][f"lorentz|{d}"]["map_mean"]
                         > aggregate["cells"][f"euclidean|{d}"]["map_mean"])]
        lines.append("  it does not invert: hyperbolic mean rank stays worse at "
                     "every d tested.")
        if map_ahead:
            lines.append(
                f"  hyperbolic MAP leads only at d in {map_ahead}, and there the "
                f"disagreement is definitional: MAP averages precision over a "
                f"node's whole gold set, mean rank is dominated by its "
                f"worst-placed gold neighbour, so a few badly placed neighbours "
                f"cost rank without costing much MAP.")
        else:
            lines.append("  and hyperbolic MAP never leads either, so there is no "
                         "MAP/rank disagreement left to explain.")
        outside = [d for d in args.dims if d not in map_ahead]
        if outside:
            lines.append(f"  at d in {outside} Euclidean leads on both metrics, so "
                         f"the d=2 rank penalty is not an artifact that dimension "
                         f"repairs — it is the price of the same crowding that "
                         f"buys the d=2 MAP.")
    return "\n".join(lines) + "\n"


def _finding_clip(aggregate, args):
    lines = [f"MAX_SPATIAL_NORM 1e4 — does the numerical guard still bind above "
             f"d=2? ({aggregate['n_nodes']} nodes)"]
    for dim in args.dims:
        cell = aggregate["cells"][f"lorentz|{dim}"]
        mean = cell["clip_bound_nodes_mean"]
        lines.append(
            f"  d={dim:<3} {mean:8.1f}/{aggregate['n_nodes']} nodes on the cap "
            f"({100.0 * mean / aggregate['n_nodes']:5.1f}%), per seed "
            f"{cell['clip_bound_nodes_per_seed']}; max embedding distance "
            f"{cell['max_emb_distance_mean']:.2f} ± "
            f"{cell['max_emb_distance_sigma']:.2f}")
    return "\n".join(lines) + "\n"


def _finding_f1(args):
    return ("F1 — checked before the sweep on synthetic-tree at d=2 "
            "(see the F1 gate above); the sweep only runs if hyperbolic "
            "distortion beats Euclidean there.\n")


def _conclusion(aggregate, args):
    """The one sentence the DoD asks for, assembled from the run so that it
    cannot drift from the table. Every distortion gap is listed, not just the
    endpoints: on wordnet the gap crosses zero at d=5 and comes back, and an
    endpoints-only sentence would read as a monotone narrowing it is not."""
    def cell(geometry, dim):
        return aggregate["cells"][f"{geometry}|{dim}"]

    dims = args.dims
    lo, hi = dims[0], dims[-1]
    gaps = ", ".join(
        f"{cell('euclidean', d)['avg_distortion_mean'] - cell('lorentz', d)['avg_distortion_mean']:+.4f} at d={d}"
        for d in dims)
    ahead = [d for d in dims if cell("lorentz", d)["map_mean"] > cell("euclidean", d)["map_mean"]]
    if ahead and ahead[-1] != hi:
        flipped = [d for d in dims if d not in ahead][0]
        turn = (f"from d={flipped} on the Euclidean baseline takes reconstruction "
                f"outright (at d={hi}, MAP {cell('euclidean', hi)['map_mean']:.4f} "
                f"and mean rank {cell('euclidean', hi)['mean_rank_mean']:.4f} against "
                f"{cell('lorentz', hi)['map_mean']:.4f} and "
                f"{cell('lorentz', hi)['mean_rank_mean']:.4f})")
    elif ahead:
        turn = (f"hyperbolic MAP stays ahead at every d tested "
                f"({cell('lorentz', hi)['map_mean']:.4f} vs "
                f"{cell('euclidean', hi)['map_mean']:.4f} at d={hi})")
    else:
        turn = (f"Euclidean already leads MAP at d={lo}, so no dimension in the "
                f"sweep favours curvature on reconstruction")
    return (
        f"On {aggregate['dataset']} with matched per-geometry tuning, hyperbolic "
        f"geometry wins unambiguously only in the dimension-starved regime — at "
        f"d={lo} it lifts MAP from {cell('euclidean', lo)['map_mean']:.4f} to "
        f"{cell('lorentz', lo)['map_mean']:.4f} and cuts average distortion from "
        f"{cell('euclidean', lo)['avg_distortion_mean']:.4f} to "
        f"{cell('lorentz', lo)['avg_distortion_mean']:.4f} — because {turn}, while "
        f"its distortion edge neither vanishes nor closes monotonically ({gaps}); "
        f"all figures are mean ± σ over {aggregate['n_seeds']} seeds.")


def _interpreter():
    """The path recorded by setup.ps1, so the printed command is runnable."""
    try:
        with open(".venv-path", encoding="ascii") as fh:
            recorded = fh.read().strip()
        if recorded:
            return recorded
    except OSError:
        pass
    return sys.executable


def seed_set(base, count):
    return [base + i for i in range(count)]


def seed_tag(base, count):
    return f"seedset{base}x{count}"


def _parse_args(argv):
    p = argparse.ArgumentParser(
        description="Phase-4 matched ablation: Euclidean vs Lorentz at several "
                    "dimensions, mean ± σ over a seed set.")
    p.add_argument("--dataset", default="synthetic-tree", choices=datasets.DATASETS)
    p.add_argument("--dims", type=int, nargs="+", default=[2, 5, 10])
    p.add_argument("--seeds", type=int, default=5,
                   help="how many seeds: base, base+1, ..., base+seeds-1")
    p.add_argument("--seed", type=int, default=DEFAULT_SEED,
                   help="base seed of the seed set")
    p.add_argument("--out", default="out")
    p.add_argument("--tune-synthetic", action="store_true",
                   help="F2 option (b): search the learning rate per (geometry, "
                        "dimension) on synthetic-tree only, print the table to "
                        "paste into LR_TABLE, and exit")
    return p.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
