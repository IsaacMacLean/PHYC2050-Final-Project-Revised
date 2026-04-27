import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, FFMpegWriter

from round_core import run_roundabout_sim, ARM_COLORS
from step4_roundabout_demo import draw_base_roads


LANE_OFFSET = 3.0
BLEND_ZONE = 8.0
ASPHALT_OUTER = 18.5


def lane_position(c):
    x, y = c["x"], c["y"]
    state = c["state"]
    if state == "circle":
        return x, y

    theta = c["theta"]
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    perp = (-sin_t, cos_t) if state == "approach" else (sin_t, -cos_t)

    r = math.hypot(x, y)
    s = max(0.0, min(1.0, (r - ASPHALT_OUTER) / BLEND_ZONE))
    return x + LANE_OFFSET * s * perp[0], y + LANE_OFFSET * s * perp[1]


def main():
    out = run_roundabout_sim(
        rate_h=0.12, rate_v=0.08, opposite=True,
        T=140.0, dt=0.1, seed=3,
        record=True, record_stride=3,
    )
    radius = out["radius"]
    extent = out["road_length"] + 8.0
    frames = out["frames"]

    max_frames = 320
    if len(frames) > max_frames:
        keep = np.linspace(0, len(frames) - 1, max_frames).astype(int)
        frames = [frames[i] for i in keep]

    fig, ax = plt.subplots(figsize=(8, 8), dpi=120)
    ax.set_aspect("equal")
    ax.set_xlim(-extent, extent)
    ax.set_ylim(-extent, extent)
    ax.set_xticks([]); ax.set_yticks([])
    draw_base_roads(ax, radius=radius, extent=extent, road_width=14.0)

    handles = []
    for arm in range(4):
        h, = ax.plot([], [], "o", ms=8, color=ARM_COLORS[arm],
                     label=f"arm {arm} ({['E', 'N', 'W', 'S'][arm]})")
        handles.append(h)
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.85)

    max_cars = max((len(snap["cars"]) for snap in frames), default=0)
    car_dots = [ax.plot([], [], "o", ms=8, zorder=10)[0] for _ in range(max_cars)]

    title = ax.text(0.5, 0.97, "", transform=ax.transAxes,
                    ha="center", va="top", fontsize=12,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.85))

    def init():
        for dot in car_dots:
            dot.set_data([], [])
            dot.set_alpha(0.0)
        title.set_text("")
        return car_dots + [title]

    def update(idx):
        snap = frames[idx]
        for dot in car_dots:
            dot.set_data([], [])
            dot.set_alpha(0.0)
        for dot, c in zip(car_dots, snap["cars"]):
            x, y = lane_position(c)
            dot.set_data([x], [y])
            dot.set_color(c["color"])
            dot.set_alpha(1.0)
        title.set_text(f"Four-arm roundabout (t = {snap['time']:.0f} s)")
        return car_dots + [title]

    anim = FuncAnimation(fig, update, frames=len(frames), init_func=init,
                         interval=60, blit=True)
    writer = FFMpegWriter(fps=16, bitrate=3200,
                          extra_args=["-pix_fmt", "yuv420p"])
    anim.save("../animations/roundabout.mp4", writer=writer, dpi=120,
              savefig_kwargs={"facecolor": "white"})
    plt.close(fig)


if __name__ == "__main__":
    main()
