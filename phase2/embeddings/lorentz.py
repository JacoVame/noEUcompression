"""Learned hyperbolic embedding (Phase 3) — Lorentz model, RiemannianAdam.

Matched ablation against `embeddings/euclidean.py` (F2): identical objective,
identical full-negative filtering, identical initialisation scale, identical
float64. Exactly two things change, and they are the two things the experiment
is about:

  * the metric — geodesic distance on the hyperboloid
    d(x, y) = arcosh(-<x, y>_L), with <u, v>_L = -u0 v0 + sum_i ui vi and
    every point constrained to the upper sheet <x, x>_L = -1 (k = 1);
  * the optimiser — `geoopt.optim.RiemannianAdam` on a `ManifoldParameter`,
    with its own learning rate and epoch budget (see below).

The ambient array is (n, dim + 1): `dim` is the *intrinsic* dimension, so
`--dim 2` is H^2 living in R^3, the same 2 degrees of freedom the Euclidean
baseline gets at `--dim 2`. Optimisation stays on the Lorentz manifold; the
Poincaré ball is visualisation only (locked decision 1).

Objective — reconstruction loss of Nickel & Kiela (2017), verbatim from the
baseline: for every directed edge (u, v), push v to the top of u's ranking
against Neg(u) = every node that is neither u nor a graph neighbour of u,

    L = mean over directed edges of  -log  exp(-d(u, v))
                                          -------------------------------
                                          exp(-d(u, v)) + sum   exp(-d(u, w))
                                                            w in Neg(u)

Negatives in full, not sampled, for the same reason as in the baseline: the
whole distance matrix fits in one step at these sizes.

Hyperparameters below were tuned on `synthetic-tree` only; `wordnet-mammals` is
the report set and never informed them.

    python eval.py --embedding lorentz --dataset synthetic-tree --dim 2 --seed 20260716
"""
import geoopt
import numpy as np
import torch
from geoopt.manifolds.lorentz.math import arcosh

# Tuned on synthetic-tree (see module docstring) over lr in {0.003, 0.005, 0.01,
# 0.02, 0.03, 0.1, 0.3, 1.0} x epochs in {1500, 3000, 4500, 6000} at d=2, best
# mean MAP over seeds {20260716, 12345, 777}: 0.9305 here, against 0.9261 at
# lr=0.01, 0.9191 at 0.03, 0.9092 at 0.1, 0.7733 at 0.3, and divergence at 1.0
# (a step of unit Minkowski length is too long for this manifold). An interior
# maximum, three orders of magnitude away from the unstable end of the grid.
# Hyperbolic-only: the Euclidean baseline keeps its own lr 0.5 / 6000 epochs,
# which is what makes the comparison matched rather than rigged (F2).
LEARNING_RATE = 0.005
EPOCHS = 6000
INIT_SCALE = 1e-3
EPS = 1e-12
CURVATURE = 1.0  # k in geoopt's parametrisation: the unit hyperboloid

# Numerical guard, not a capacity knob (Nickel & Kiela 2018, "numerical
# stability"): the softmax objective is unbounded in radius — inflating the
# global scale always lowers the loss — and on the hyperboloid the ambient
# coordinates grow like cosh(d), so an unconstrained run walks out of float64.
# At |x_1:d| = 1e4 the Minkowski products reach ~1e8, which still leaves ~8
# significant digits, so the constraint <x,x>_L = -1 stays representable
# (residual ~1e-8). Left free, the same run reaches 1e6 in 5500 epochs, the
# residual degrades to 2e-4 and geoopt's retraction emits NaN.
#
# It binds — 149/364 synthetic nodes and 711/1170 wordnet nodes sit on it — but
# it does not manufacture the result: on synthetic-tree at d=2/seed 20260716 the
# MAP is 0.9222 / 0.9220 / 0.9222 at caps 1e3 / 1e4 / 1e5, and at 1e5 no node
# reaches the cap at all. Only a crippling 1e2 (max distance 10.6, under the
# graph diameter) changes the answer, to 0.7940. 1e4 is the flat interior.
MAX_SPATIAL_NORM = 1e4


def build(hierarchy, dim, seed):
    """Return (coords, emb_dist) for the harness.

    coords   : (n, dim + 1) float64 array of hyperboloid positions, time
               coordinate first
    emb_dist : (n, n) symmetric non-negative array of geodesic distances in H^dim
    """
    torch.manual_seed(seed)
    generator = torch.Generator().manual_seed(seed)
    n = hierarchy.n

    manifold = geoopt.Lorentz(k=CURVATURE)
    ambient = torch.empty((n, dim + 1), dtype=torch.float64)
    ambient.normal_(0.0, INIT_SCALE, generator=generator)
    # projx recomputes the time coordinate from the spatial part, so the init is
    # the baseline's Gaussian cloud lifted onto the sheet near its apex.
    coords = geoopt.ManifoldParameter(manifold.projx(ambient), manifold=manifold)

    src, dst = _directed_edges(hierarchy)
    neg_mask = _negative_mask(hierarchy)
    # stabilize=1 re-projects the transported momentum onto the tangent space
    # every step. Without it the running average accumulates a component along
    # the light cone that the Minkowski norm cannot see (ambient magnitude 1e100
    # at a reported length of 1e-4, the clamp floor in geoopt's `_norm`), and the
    # retraction takes an astronomically long step. Numerical hygiene, not a knob.
    optimizer = geoopt.optim.RiemannianAdam([coords], lr=LEARNING_RATE, stabilize=1)

    for _ in range(EPOCHS):
        optimizer.zero_grad()
        dist = _pairwise(coords)
        loss = _ranking_loss(dist, src, dst, neg_mask)
        loss.backward()
        optimizer.step()
        _clip_radius(coords, manifold)

    with torch.no_grad():
        final = _pairwise(coords)
        final = 0.5 * (final + final.T)
        final.fill_diagonal_(0.0)
    return coords.detach().numpy(), final.numpy()


def _clip_radius(coords, manifold):
    """Keep every point inside the well-conditioned patch of the hyperboloid.

    Shrinks the spatial part to `MAX_SPATIAL_NORM` where it exceeds it, then
    re-projects so the time coordinate is again sqrt(1 + |x_1:d|^2).
    """
    with torch.no_grad():
        space = coords[:, 1:]
        # a zero-norm row gives inf, which clamps straight back to 1.0
        space.mul_((MAX_SPATIAL_NORM / space.norm(dim=1, keepdim=True)).clamp(max=1.0))
        coords.copy_(manifold.projx(coords))


def _pairwise(coords):
    """All-pairs geodesic distance, arcosh of the negated Minkowski Gram matrix.

    Equivalent to `geoopt.Lorentz(k=1).dist(coords[:, None], coords[None, :])`
    (checked to float64 tolerance) but computed as two matmuls instead of an
    (n, n, dim + 1) broadcast, which keeps WordNet-sized runs in cache.
    """
    time = coords[:, :1]
    space = coords[:, 1:]
    gram = time @ time.T - space @ space.T          # -<x, y>_L, >= 1 on the sheet
    # clamp: arcosh'(1) is infinite, exactly as sqrt'(0) is in the baseline
    return arcosh(torch.clamp(gram, min=1.0 + EPS))


def _ranking_loss(dist, src, dst, neg_mask):
    """-log softmax of the gold neighbour against all non-neighbours."""
    # scalar rather than full_like: same values bit for bit, one (n, n) float64
    # allocation fewer per epoch (11 MB at wordnet size, 6000 epochs)
    neg_logits = torch.where(neg_mask, -dist, -torch.inf)
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
