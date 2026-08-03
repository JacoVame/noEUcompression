"""Metrics for the eval harness — FROZEN after Phase 1.

Every metric takes an (n, n) matrix of *embedding* distances and compares it
against the graph metric of a `Hierarchy`. The harness never learns anything
and never touches a manifold: geometry lives entirely inside whatever produced
`emb_dist`. That is the whole point of building this before the embeddings.

Definitions used here
---------------------
MAP        reconstruction MAP of Nickel & Kiela (2017): for every node, its
           gold set is its direct graph neighbours (parent + children); each
           gold node is ranked against the *non*-neighbours only (filtered
           ranking), and the per-node average precisions are averaged.
mean rank  mean filtered rank of a gold neighbour. 1.0 is perfect.
avg        mean over unordered pairs of |a*d_emb/d_graph - 1|, at the global
distortion scale `a` that minimises it. Scaling is mandatory, not a favour:
           without it the number measures the arbitrary radius of the
           embedding rather than its shape, and Euclidean-vs-hyperbolic
           becomes a comparison of units. The minimiser is exact (a weighted
           median, see `optimal_scale`), so no optimiser and no tuning enter
           the harness.
"""
import numpy as np


def evaluate(hierarchy, emb_dist):
    """Run every metric. Returns a plain dict (JSON-serialisable scalars plus
    the two curves the plots need)."""
    emb_dist = np.asarray(emb_dist, dtype=np.float64)
    n = hierarchy.n
    if emb_dist.shape != (n, n):
        raise ValueError(f"emb_dist must be {(n, n)}, got {emb_dist.shape}")
    if not np.isfinite(emb_dist).all():
        raise ValueError("emb_dist contains non-finite values")

    mean_ap, mean_rank = map_and_mean_rank(hierarchy.neighbors, emb_dist)
    scale = optimal_scale(hierarchy.graph_dist, emb_dist)
    terms = _pair_distortion(hierarchy.graph_dist, emb_dist, scale)
    levels, by_depth, counts = distortion_by_depth(hierarchy, terms)

    iu = np.triu_indices(n, 1)
    return {
        "n_nodes": n,
        "n_pairs": int(iu[0].size),
        "map": float(mean_ap),
        "mean_rank": float(mean_rank),
        "avg_distortion": float(terms.mean()),
        "distortion_scale": float(scale),
        "depth_levels": [int(x) for x in levels],
        "distortion_by_depth": [float(x) for x in by_depth],
        "pairs_by_depth": [int(x) for x in counts],
        "emb_dist_pairs": emb_dist[iu] * scale,   # scaled, for the histogram
        "graph_dist_pairs": hierarchy.graph_dist[iu],
    }


def map_and_mean_rank(neighbors, emb_dist):
    """Filtered MAP and mean rank of the gold neighbours."""
    n = emb_dist.shape[0]
    ap_total = 0.0
    rank_total = 0.0
    rank_count = 0
    for u in range(n):
        gold = np.fromiter(neighbors[u], dtype=np.int64, count=len(neighbors[u]))
        if gold.size == 0:
            continue
        row = emb_dist[u]
        is_neg = np.ones(n, dtype=bool)
        is_neg[u] = False
        is_neg[gold] = False
        neg = np.sort(row[is_neg])
        # rank = 1 + number of non-neighbours strictly closer than the gold node
        ranks = np.searchsorted(neg, row[gold], side="left") + 1
        ranks.sort()
        # the i-th gold node sits at position rank_i + i - 1 in the full list
        # (rank_i counts negatives only), so precision there is i / that.
        found = np.arange(1, ranks.size + 1)
        ap_total += float(np.mean(found / (ranks + found - 1)))
        rank_total += float(ranks.sum())
        rank_count += ranks.size
    return ap_total / n, rank_total / rank_count


def optimal_scale(graph_dist, emb_dist):
    """Global scale `a` minimising mean |a*d_emb/d_graph - 1| over pairs.

    Writing w = d_emb/d_graph and t = d_graph/d_emb, each term is
    w*|a - t|, so the minimiser is the w-weighted median of t. Exact, closed
    form, no tuning knob.
    """
    iu = np.triu_indices(graph_dist.shape[0], 1)
    dg = graph_dist[iu]
    de = emb_dist[iu]
    ok = de > 0
    if not ok.any():
        return 1.0
    w = de[ok] / dg[ok]
    t = dg[ok] / de[ok]
    order = np.argsort(t, kind="stable")
    cumulative = np.cumsum(w[order])
    if cumulative[-1] <= 0:
        return 1.0
    pos = int(np.searchsorted(cumulative, 0.5 * cumulative[-1], side="left"))
    return float(t[order][pos])


def distortion_by_depth(hierarchy, pair_terms):
    """Mean distortion of pairs bucketed by the depth of the deeper endpoint.

    This is the curve that should separate the geometries: Euclidean space at
    low d runs out of room as the tree deepens, hyperbolic space does not.
    """
    iu = np.triu_indices(hierarchy.n, 1)
    depth = np.maximum(hierarchy.depths[iu[0]], hierarchy.depths[iu[1]])
    levels = np.unique(depth)
    means = np.array([pair_terms[depth == k].mean() for k in levels])
    counts = np.array([int((depth == k).sum()) for k in levels])
    return levels, means, counts


def _pair_distortion(graph_dist, emb_dist, scale):
    iu = np.triu_indices(graph_dist.shape[0], 1)
    return np.abs(scale * emb_dist[iu] / graph_dist[iu] - 1.0)
