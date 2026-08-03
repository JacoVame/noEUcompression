"""Figures for the eval harness — FROZEN after Phase 1.

Two plots, both required by the Phase-1 DoD and both reused as money plots in
Phase 4: the crowding histogram (distance-distribution spread) and the
distortion-vs-depth curve. Every filename embeds the seed; the caller builds
the path.
"""
import matplotlib
import numpy as np

matplotlib.use("Agg")  # headless: no display on the build host
import matplotlib.pyplot as plt  # noqa: E402

HIST_BINS = 40


def crowding_histogram(path, emb_dist_pairs, graph_dist_pairs, title):
    """Distribution of scaled embedding distances against the graph metric.

    Crowding shows up as an embedding histogram far narrower than the graph
    one: many tree distances collapsed onto the same radius.
    """
    fig, ax = plt.subplots(figsize=(7, 4.2))
    # hops are integers: bin them on integer edges, or 40 fixed-width bins
    # alias into a comb and the comparison becomes unreadable.
    hop_edges = np.arange(graph_dist_pairs.min() - 0.5,
                          graph_dist_pairs.max() + 1.5)
    ax.hist(graph_dist_pairs, bins=hop_edges, density=True, alpha=0.45,
            label="graph distance (hops)", color="#888888")
    ax.hist(emb_dist_pairs, bins=HIST_BINS, density=True, alpha=0.65,
            label="embedding distance (scaled)", color="#1f77b4")
    ax.set_xlabel("pairwise distance")
    ax.set_ylabel("density")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path


def depth_curve(path, levels, distortion, counts, title):
    """Mean distortion per depth bucket, annotated with the pair count."""
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(levels, distortion, marker="o", color="#d62728")
    ax.set_xlabel("depth of the deeper endpoint (hops from root)")
    ax.set_ylabel("mean distortion  |a*d_emb/d_graph - 1|")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.set_xticks(list(levels))
    twin = ax.twinx()
    twin.bar(levels, counts, alpha=0.15, color="#7f7f7f", width=0.6)
    twin.set_ylabel("pairs in bucket")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return path
