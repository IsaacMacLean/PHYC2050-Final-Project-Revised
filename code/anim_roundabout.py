import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, FFMpegWriter

from round_core import run_roundabout_sim, ARM_COLORS
from step4_roundabout_demo import draw_base_roads


def main():
    out = run_roundabout_sim(
        rate_h=0.10, rate_v=0.10, opposite=True,
        T=120.0, dt=0.1, seed=3,
        record=True, record_stride=2,
    )
    radius = out["radius"]
    extent = out["road_length"] + 8.0
    frames = out["frames"]
    lane_offset = 3.0

    fig = plt.figure(figsize=(8, 8), dpi=120)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_xticks([]); ax.set_yticks([])
    draw_base_roads(ax, radius=radius, extent=extent, road_width=14.0)

    handles = []
    for arm in range(4):
        h = ax.scatter([], [], s=70, c=ARM_COLORS[arm], edgecolor="black", lw=0.6,
                       label=f"arm {arm} ({['E', 'N', 'W', 'S'][arm]})")
        handles.append(h)
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.85)

    scat = ax.scatter(np.zeros(0), np.zeros(0), s=70,
                      edgecolor="black", lw=0.6, zorder=10)
    title = ax.text(0.5, 0.97, "", transform=ax.transAxes,
                    ha="center", va="top", fontsize=12,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.85))

    def positions(snap):
        xs, ys, cs = [], [], []
        for c in snap["cars"]:
            x, y = c["x"], c["y"]
            theta = c.get("theta", math.atan2(y, x))
            nx, ny = -math.sin(theta), math.cos(theta)
            if c["state"] == "approach":
                x += lane_offset * nx; y += lane_offset * ny
            elif c["state"] == "exit":
                x -= lane_offset * nx; y -= lane_offset * ny
            xs.append(x); ys.append(y); cs.append(c["color"])
        return xs, ys, cs

    def update(idx):
        snap = frames[idx]
        xs, ys, cs = positions(snap)
        if xs:
            scat.set_offsets(np.column_stack([xs, ys]))
            scat.set_facecolors(cs)
        else:
            scat.set_offsets(np.empty((0, 2)))
            scat.set_facecolors([])
        title.set_text(f"Four-arm roundabout (t = {snap['time']:.0f} s)")
        return scat, title

    anim = FuncAnimation(fig, update, frames=len(frames), interval=40, blit=False)
    writer = FFMpegWriter(fps=25, bitrate=2400,
                          extra_args=["-pix_fmt", "yuv420p"])
    anim.save("../animations/roundabout.mp4", writer=writer, dpi=120,
              savefig_kwargs={"facecolor": "white"})
    plt.close(fig)


if __name__ == "__main__":
    main()
