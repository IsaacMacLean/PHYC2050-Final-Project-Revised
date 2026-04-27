import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle

from round_core import run_roundabout_sim, ARM_COLORS, TWOPI, arm_angle


LANE_OFFSET = 3.0
CIRCLE_BLEND_ARC = 12.0
ARM_BLEND_RADIAL = 18.0


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def approach_lane_vector(theta):
    return -math.sin(theta), math.cos(theta)


def exit_lane_vector(theta):
    return math.sin(theta), -math.cos(theta)


def blended_arm_radius(r, radius):
    dr = max(0.0, r - radius)
    if dr >= ARM_BLEND_RADIAL:
        return r
    return radius + dr * smoothstep(dr / ARM_BLEND_RADIAL)


def offset_arm_position(theta, r, offset_vec, radius):
    visual_r = blended_arm_radius(r, radius)
    return (
        visual_r * math.cos(theta) + LANE_OFFSET * offset_vec[0],
        visual_r * math.sin(theta) + LANE_OFFSET * offset_vec[1],
    )


def lane_position(c, radius=15.0):
    x, y = c["x"], c["y"]
    state = c["state"]
    theta = c["theta"]

    if state == "approach":
        return offset_arm_position(
            theta, math.hypot(x, y), approach_lane_vector(theta), radius
        )

    if state == "exit":
        return offset_arm_position(
            theta, math.hypot(x, y), exit_lane_vector(theta), radius
        )

    if state != "circle":
        return x, y

    entry_theta = arm_angle(c["arm"])
    exit_theta = arm_angle(c.get("exit_arm", (c["arm"] + 2) % 4))
    blend_angle = CIRCLE_BLEND_ARC / max(radius, 1e-9)
    travelled = (theta - entry_theta) % TWOPI
    remaining = (exit_theta - theta) % TWOPI

    if travelled < blend_angle:
        weight = 1.0 - smoothstep(travelled / blend_angle)
        ox, oy = approach_lane_vector(entry_theta)
    elif remaining < blend_angle:
        weight = 1.0 - smoothstep(remaining / blend_angle)
        ox, oy = exit_lane_vector(exit_theta)
    else:
        return x, y

    return x + LANE_OFFSET * weight * ox, y + LANE_OFFSET * weight * oy


def draw_base_roads(ax, radius=15.0, extent=105.0, road_width=14.0):
    ax.add_patch(Rectangle((-extent, -extent), 2 * extent, 2 * extent,
                           facecolor="#cfe7c4", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-extent, -road_width / 2), 2 * extent, road_width,
                           facecolor="#a9a9a9", edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((-road_width / 2, -extent), road_width, 2 * extent,
                           facecolor="#a9a9a9", edgecolor="none", zorder=1))

    ring_half = road_width / 4.0
    gap = radius + ring_half
    for sgn in (-1, 1):
        ax.plot([sgn * extent, sgn * gap], [0, 0],
                ls="--", color="#444", lw=1.4, dashes=(6, 6), zorder=2)
        ax.plot([0, 0], [sgn * extent, sgn * gap],
                ls="--", color="#444", lw=1.4, dashes=(6, 6), zorder=2)

    ax.add_patch(Circle((0, 0), radius + ring_half,
                        facecolor="#7d7d7d", edgecolor="none", zorder=3))
    ax.add_patch(Circle((0, 0), max(radius - ring_half, 0.5),
                        facecolor="#5d8a48", edgecolor="black", lw=1.0, zorder=4))
    theta = np.linspace(0, 2 * math.pi, 200)
    ax.plot(radius * np.cos(theta), radius * np.sin(theta),
            color="white", lw=1.0, zorder=5)


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

    if snap["cars"]:
        xs, ys, cs = [], [], []
        for c in snap["cars"]:
            x, y = lane_position(c, radius=radius)
            xs.append(x); ys.append(y); cs.append(c["color"])
        ax.scatter(xs, ys, s=70, c=cs, edgecolor="black", lw=0.6, zorder=10)

    handles = []
    for arm in range(4):
        h = ax.scatter([], [], s=70, c=ARM_COLORS[arm], edgecolor="black", lw=0.6,
                       label=f"arm {arm} ({['E', 'N', 'W', 'S'][arm]})")
        handles.append(h)
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.85)

    ax.set_title(f"Four-arm roundabout, all four arms emitting (t = {t_show:.0f} s)",
                 fontsize=12)
    plt.tight_layout()
    plt.savefig("../figures/fig_step4_roundabout.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
