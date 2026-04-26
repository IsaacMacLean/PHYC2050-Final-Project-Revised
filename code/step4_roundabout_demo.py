import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle

from round_core import run_roundabout_sim
from step3_intersection_lights import ASPHALT, CENTER, EDGE, GRASS


def _plot_segments(ax, segments, **kw):
    for x0, y0, x1, y1 in segments:
        ax.plot([x0, x1], [y0, y1], **kw)


def draw_base_roads(ax, radius=15.0, extent=105.0, road_width=24.0):
    ax.add_patch(Rectangle((-extent, -extent), 2 * extent, 2 * extent,
                           facecolor=GRASS, edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-extent, -road_width / 2), 2 * extent, road_width,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((-road_width / 2, -extent), road_width, 2 * extent,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))

    ring_half = road_width / 2.0
    gap = radius + ring_half
    edge_segments = []
    for sgn in (-1, 1):
        edge_segments += [
            (sgn * extent, road_width / 2, sgn * gap, road_width / 2),
            (sgn * extent, -road_width / 2, sgn * gap, -road_width / 2),
            (road_width / 2, sgn * extent, road_width / 2, sgn * gap),
            (-road_width / 2, sgn * extent, -road_width / 2, sgn * gap),
        ]
    _plot_segments(ax, edge_segments, color=EDGE, lw=1.0, zorder=2)

    for x0 in np.arange(-extent, extent, 16):
        if abs(x0 + 4) > gap:
            ax.plot([x0, x0 + 8], [0, 0], color=CENTER, lw=1.5, zorder=2)
    for y0 in np.arange(-extent, extent, 16):
        if abs(y0 + 4) > gap:
            ax.plot([0, 0], [y0, y0 + 8], color=CENTER, lw=1.5, zorder=2)

    ax.add_patch(Circle((0, 0), radius + ring_half,
                        facecolor=ASPHALT, edgecolor=EDGE, lw=1.0, zorder=3))
    ax.add_patch(Circle((0, 0), max(radius - ring_half, 0.5),
                        facecolor=GRASS, edgecolor=EDGE, lw=1.0, zorder=4))
    theta = np.linspace(0, 2 * math.pi, 200)
    ax.plot((radius + ring_half) * np.cos(theta),
            (radius + ring_half) * np.sin(theta),
            color=EDGE, lw=1.0, zorder=5)
    ax.plot(max(radius - ring_half, 0.5) * np.cos(theta),
            max(radius - ring_half, 0.5) * np.sin(theta),
            color=EDGE, lw=1.0, zorder=5)
    ax.plot(radius * np.cos(theta), radius * np.sin(theta),
            color=CENTER, lw=1.5, dashes=(6, 6), zorder=5)

    arrow = dict(arrowstyle="-|>", color="white", lw=2.2,
                 mutation_scale=14)
    label_box = dict(facecolor="black", edgecolor="none", alpha=0.45,
                     boxstyle="round,pad=0.2")
    ax.annotate("", xy=(-55, -34), xytext=(-85, -34),
                arrowprops=arrow, zorder=7)
    ax.text(-70, -50, "H flow", color="white", fontsize=10,
            ha="center", va="center", bbox=label_box, zorder=7)
    ax.annotate("", xy=(34, -55), xytext=(34, -85),
                arrowprops=arrow, zorder=7)
    ax.text(50, -70, "V flow", color="white", fontsize=10,
            ha="center", va="center", rotation=90, bbox=label_box, zorder=7)


def main():
    out = run_roundabout_sim(
        rate_h=0.10, rate_v=0.10, opposite=True,
        T=140.0, dt=0.1, seed=3,
        record=True, record_stride=5,
    )
    radius = out["radius"]
    extent = out["road_length"] + 8.0

    snap = out["frames"][-1]
    t_show = snap["time"]

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_aspect("equal")
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_xticks([])
    ax.set_yticks([])

    draw_base_roads(ax, radius=radius, extent=extent)

    lane_offset = 3.0
    if snap["cars"]:
        xs, ys, cs = [], [], []
        for c in snap["cars"]:
            x, y = c["x"], c["y"]
            theta = c.get("theta")
            if theta is None:
                theta = math.atan2(y, x)
            nx, ny = -math.sin(theta), math.cos(theta)
            if c["state"] == "approach":
                x += lane_offset * nx
                y += lane_offset * ny
            elif c["state"] == "exit":
                x -= lane_offset * nx
                y -= lane_offset * ny
            xs.append(x); ys.append(y); cs.append(c["color"])
        ax.scatter(xs, ys, marker="s", s=180, c=cs,
                   edgecolor="black", lw=0.6, zorder=10)

    ax.set_title(f"Four-arm roundabout, all four arms emitting (t = {t_show:.0f} s)",
                 fontsize=12)
    plt.tight_layout()
    plt.savefig("../figures/fig_step4_roundabout.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
