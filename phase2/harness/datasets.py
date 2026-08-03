"""Datasets for the eval harness — FROZEN after Phase 1.

A dataset is a rooted tree exposed as a `Hierarchy`. Everything downstream
(metrics, plots, embeddings) sees only that object: this module is the only
place that knows about WordNet or about how a synthetic tree is shaped.

Both trees are deterministic by construction, so `--seed` changes the
embedding, never the ground truth. That is what makes the F3 claim
("same seed + same command => same numbers") checkable.
"""
from collections import deque
from dataclasses import dataclass, field

import numpy as np

DATASETS = ("synthetic-tree", "wordnet-mammals")

# Synthetic tree shape: fixed constants, not knobs (no config systems).
SYNTHETIC_BRANCHING = 3
SYNTHETIC_DEPTH = 5


@dataclass
class Hierarchy:
    """A rooted tree plus its graph metric.

    name       : dataset identifier
    names      : node labels, index-aligned with every array below
    parents    : parent index per node, -1 for the root
    depths     : hop distance from the root
    neighbors  : undirected adjacency (parent + children) as index sets
    graph_dist : (n, n) all-pairs shortest-path distance in hops
    """

    name: str
    names: list
    parents: np.ndarray
    depths: np.ndarray
    neighbors: list
    graph_dist: np.ndarray
    root: int = 0
    edges: list = field(default_factory=list)

    @property
    def n(self):
        return len(self.names)


def load(name, seed=None):
    """Return the `Hierarchy` for `name`. `seed` is accepted and unused:
    the ground truth is deterministic (see module docstring)."""
    if name == "synthetic-tree":
        names, parents = _synthetic_tree(SYNTHETIC_BRANCHING, SYNTHETIC_DEPTH)
    elif name == "wordnet-mammals":
        names, parents = _wordnet_mammals()
    else:
        raise ValueError(f"unknown dataset {name!r}; expected one of {DATASETS}")
    return _build(name, names, parents)


def _synthetic_tree(branching, depth):
    """Balanced tree, breadth-first node order, root first."""
    names = ["n0"]
    parents = [-1]
    frontier = [0]
    for _ in range(depth):
        nxt = []
        for p in frontier:
            for _ in range(branching):
                nxt.append(len(names))
                names.append(f"n{len(names)}")
                parents.append(p)
        frontier = nxt
    return names, parents


def _wordnet_mammals():
    """`mammal.n.01` and its hyponym closure.

    WordNet hypernymy is a DAG (a few synsets have two hypernyms). A
    breadth-first sweep with children visited in name order turns it into a
    tree deterministically: the first visit fixes the parent.
    """
    from nltk.corpus import wordnet as wn

    root = wn.synset("mammal.n.01")
    names = [root.name()]
    index = {root.name(): 0}
    parents = [-1]
    queue = deque([root])
    while queue:
        synset = queue.popleft()
        p = index[synset.name()]
        for child in sorted(synset.hyponyms(), key=lambda s: s.name()):
            if child.name() in index:
                continue  # already reached by a shorter/earlier path
            index[child.name()] = len(names)
            names.append(child.name())
            parents.append(p)
            queue.append(child)
    return names, parents


def _build(name, names, parents):
    parents = np.asarray(parents, dtype=np.int64)
    n = len(names)
    if int((parents == -1).sum()) != 1 or parents[0] != -1:
        raise ValueError("expected exactly one root, at index 0")

    neighbors = [set() for _ in range(n)]
    edges = []
    for child in range(1, n):
        p = int(parents[child])
        neighbors[p].add(child)
        neighbors[child].add(p)
        edges.append((p, child))

    depths = np.zeros(n, dtype=np.int64)
    for i in range(1, n):
        depths[i] = depths[parents[i]] + 1  # parents precede children (BFS order)

    return Hierarchy(
        name=name,
        names=list(names),
        parents=parents,
        depths=depths,
        neighbors=neighbors,
        graph_dist=_all_pairs_hops(neighbors),
        root=0,
        edges=edges,
    )


def _all_pairs_hops(neighbors):
    """BFS from every node. O(n^2) on a tree, fine at these sizes."""
    n = len(neighbors)
    dist = np.full((n, n), -1, dtype=np.int32)
    for source in range(n):
        row = dist[source]
        row[source] = 0
        frontier = [source]
        hop = 0
        while frontier:
            hop += 1
            nxt = []
            for u in frontier:
                for v in neighbors[u]:
                    if row[v] < 0:
                        row[v] = hop
                        nxt.append(v)
            frontier = nxt
    if (dist < 0).any():
        raise ValueError("graph is disconnected")
    return dist.astype(np.float64)
