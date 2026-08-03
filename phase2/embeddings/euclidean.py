"""Euclidean baseline (Phase 2) — the control geometry for the ablation.

Learned, not analytic: the point of the phase set is to compare *matched*
optimisations, so the baseline must be trained on the same objective that the
Lorentz model (Phase 3) will be trained on, differing only in the metric and in
the per-geometry learning rate (F2). A closed-form embedding (MDS, spectral)
would answer a different question.

Objective — the reconstruction loss of Nickel & Kiela (2017): for every edge
(u, v) of the hierarchy, push v to the top of u's ranking against every
non-neighbour of u,

    L = mean over directed edges of  -log  exp(-d(u, v))
                                          -------------------------------
                                          exp(-d(u, v)) + sum   exp(-d(u, w))
                                                            w in Neg(u)

with Neg(u) = every node that is neither u nor a graph neighbour of u. The
negatives are taken in full rather than sampled: at these tree sizes (10^2-10^3
nodes) the whole distance matrix fits in one step, which removes both a
hyperparameter and the only source of run-to-run noise beyond the init.

Hyperparameters below were tuned on `synthetic-tree` only; `wordnet-mammals` is
the report set and never informed them.

    python eval.py --embedding euclidean --dataset synthetic-tree --dim 2 --seed 20260716
"""
import numpy as np
import torch

# Tuned on synthetic-tree (see module docstring) over lr in {0.01 .. 1.0} x
# epochs in {1500 .. 6000} at d=2, best mean MAP over seeds {20260716, 12345,
# 777}. Euclidean-only: Phase 3 sets its own, which is what makes the Phase-4
# ablation matched rather than rigged.
LEARNING_RATE = 0.5
EPOCHS = 6000
INIT_SCALE = 1e-3
EPS = 1e-12


def build(hierarchy, dim, seed):
    """Return (coords, emb_dist) for the harness.

    coords   : (n, dim) float64 array of Euclidean positions
    emb_dist : (n, n) symmetric non-negative array of Euclidean distances
    """
    torch.manual_seed(seed)
    generator = torch.Generator().manual_seed(seed)
    n = hierarchy.n

    coords = torch.empty((n, dim), dtype=torch.float64)
    coords.normal_(0.0, INIT_SCALE, generator=generator)
    coords.requires_grad_(True)

    src, dst = _directed_edges(hierarchy)
    neg_mask = _negative_mask(hierarchy)
    optimizer = torch.optim.Adam([coords], lr=LEARNING_RATE)

    for _ in range(EPOCHS):
        optimizer.zero_grad()
        dist = _pairwise(coords)
        loss = _ranking_loss(dist, src, dst, neg_mask)
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        final = _pairwise(coords)
        final = 0.5 * (final + final.T)
        final.fill_diagonal_(0.0)
    return coords.detach().numpy(), final.numpy()


def _pairwise(coords):
    sq = (coords * coords).sum(dim=1)
    d2 = sq[:, None] + sq[None, :] - 2.0 * (coords @ coords.T)
    return torch.sqrt(torch.clamp(d2, min=EPS))  # clamp: sqrt'(0) is infinite


def _ranking_loss(dist, src, dst, neg_mask):
    """-log softmax of the gold neighbour against all non-neighbours."""
    neg_logits = torch.where(neg_mask, -dist, torch.full_like(dist, -torch.inf))
    neg_lse = torch.logsumexp(neg_logits, dim=1)          # per source node
    positive = -dist[src, dst]
    return (torch.logaddexp(neg_lse[src], positive) - positive).mean()


def _directed_edges(hierarchy):
    """Both orientations of every tree edge: the ranking is per source node."""
    pairs = np.array(hierarchy.edges, dtype=np.int64)
    src = torch.from_numpy(np.concatenate([pairs[:, 0], pairs[:, 1]]))
    dst = torch.from_numpy(np.concatenate([pairs[:, 1], pairs[:, 0]]))
    return src, dst


def _negative_mask(hierarchy):
    """(n, n) bool: True where the column is neither the row nor its neighbour.

    Same filtering the harness applies when it ranks (`harness/metrics.py`).
    """
    n = hierarchy.n
    mask = np.ones((n, n), dtype=bool)
    np.fill_diagonal(mask, False)
    for u, adjacent in enumerate(hierarchy.neighbors):
        mask[u, list(adjacent)] = False
    return torch.from_numpy(mask)
