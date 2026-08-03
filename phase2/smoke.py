#!/usr/bin/env python3
"""Phase 0 smoke test — binary DoD.

Verifies the three load-bearing assumptions of the whole phase set:
  1. geoopt's Lorentz manifold + RiemannianAdam actually optimize
     (a handful of points pulled toward a target: loss must drop >50%).
  2. Hyperbolic distance behaves (triangle sanity + positivity).
  3. WordNet is downloaded and the mammal.n.01 hyponym closure is usable.

Exit code 0 = OK, 1 = failure (per F3, this is the gate for Phase 1).
"""
import sys

def fail(msg):
    print(f"SMOKE FAIL: {msg}")
    sys.exit(1)

def main():
    # ---- imports
    try:
        import torch, geoopt, numpy, matplotlib
        import nltk
    except ImportError as e:
        fail(f"import error: {e} (run setup.ps1 first)")
    print(f"torch {torch.__version__} | geoopt {geoopt.__version__} | "
          f"numpy {numpy.__version__} | matplotlib {matplotlib.__version__}")

    # ---- 1. Lorentz + RiemannianAdam take real optimization steps
    torch.manual_seed(20260716)
    man = geoopt.manifolds.Lorentz()
    dim = 4  # ambient dim 4 -> hyperboloid H^3; enough for a smoke
    pts = geoopt.ManifoldParameter(
        man.projx(torch.randn(8, dim) * 0.3), manifold=man)
    target = man.projx(torch.randn(1, dim) * 0.3).detach()
    opt = geoopt.optim.RiemannianAdam([pts], lr=5e-2)

    def loss_fn():
        return man.dist(pts, target.expand_as(pts)).mean()

    l0 = loss_fn().item()
    for _ in range(120):
        opt.zero_grad()
        loss = loss_fn()
        loss.backward()
        opt.step()
    l1 = loss_fn().item()
    print(f"Lorentz optimization: loss {l0:.4f} -> {l1:.4f}")
    if not (l1 < 0.5 * l0):
        fail("RiemannianAdam did not reduce the loss by >50% "
             "(manifold optimization is broken)")
    # points must still live on the manifold
    if not torch.isfinite(pts).all():
        fail("non-finite coordinates after optimization")

    # ---- 2. distance sanity
    a, b, c = pts[0:1], pts[1:2], pts[2:3]
    dab, dbc, dac = (man.dist(a, b).item(), man.dist(b, c).item(),
                     man.dist(a, c).item())
    if min(dab, dbc, dac) < 0:
        fail("negative hyperbolic distance")
    if dac > dab + dbc + 1e-4:
        fail("triangle inequality violated")
    print(f"distance sanity: d(a,b)={dab:.3f} d(b,c)={dbc:.3f} "
          f"d(a,c)={dac:.3f} OK")

    # ---- 3. WordNet closure
    try:
        from nltk.corpus import wordnet as wn
        mammal = wn.synset("mammal.n.01")
    except LookupError:
        fail("WordNet corpus not downloaded (setup.ps1 does this)")
    closure = set(mammal.closure(lambda s: s.hyponyms()))
    print(f"WordNet mammal.n.01 hyponym closure: {len(closure)} synsets")
    if len(closure) < 500:
        fail(f"closure suspiciously small ({len(closure)}); "
             "expected ~1k+ synsets")

    print("PHASE 0 SMOKE: OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
