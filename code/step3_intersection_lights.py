import math
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from sim_core import Lane, LIGHT_STOP_LINE, Signal


GRASS = "#9bc78a"
ASPHALT = "#3b3b3b"
EDGE = "#d9d9d9"
CENTER = "#f1c40f"
STOP_LINE = "#ffffff"


def draw_flow_arrows(ax):
    arrow = dict(arrowstyle="-|>", color="white", lw=2.5,
                 mutation_scale=15)
    label_box = dict(facecolor="black", edgecolor="none", alpha=0.45,
                     boxstyle="round,pad=0.2")
    ax.annotate("", xy=(-150, -34), xytext=(-205, -34),
                arrowprops=arrow, zorder=7)
    ax.text(-178, -50, "H flow", color="white", fontsize=11,
            ha="center", va="center", bbox=label_box, zorder=7)
    ax.annotate("", xy=(34, -150), xytext=(34, -205),
                arrowprops=arrow, zorder=7)
    ax.text(52, -178, "V flow", color="white", fontsize=11,
            ha="center", va="center", rotation=90, bbox=label_box, zorder=7)


def draw_intersection(ax, road_w=24.0, span=230.0, stop_s=LIGHT_STOP_LINE):
    ax.add_patch(Rectangle((-span, -span), 2 * span, 2 * span,
                           facecolor=GRASS, edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-span, -road_w / 2), 2 * span, road_w,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.add_patch(Rectangle((-road_w / 2, -span), road_w, 2 * span,
                           facecolor=ASPHALT, edgecolor="none", zorder=1))
    ax.plot([-span, span], [road_w / 2, road_w / 2], color=EDGE, lw=1.0, zorder=2)
    ax.plot([-span, span], [-road_w / 2, -road_w / 2], color=EDGE, lw=1.0, zorder=2)
    ax.plot([road_w / 2, road_w / 2], [-span, span], color=EDGE, lw=1.0, zorder=2)
    ax.plot([-road_w / 2, -road_w / 2], [-span, span], color=EDGE, lw=1.0, zorder=2)
    for x0 in np.arange(-span, span, 16):
        if abs(x0 + 8) > road_w / 2:
            ax.plot([x0, x0 + 8], [0, 0], color=CENTER, lw=1.5, zorder=2)
    for y0 in np.arange(-span, span, 16):
        if abs(y0 + 8) > road_w / 2:
            ax.plot([0, 0], [y0, y0 + 8], color=CENTER, lw=1.5, zorder=2)
    ax.plot([-road_w / 2, road_w / 2], [-road_w / 2, -road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)
    ax.plot([-road_w / 2, road_w / 2], [road_w / 2, road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)
    ax.plot([-road_w / 2, -road_w / 2], [-road_w / 2, road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)
    ax.plot([road_w / 2, road_w / 2], [-road_w / 2, road_w / 2],
            color=STOP_LINE, lw=3, zorder=3)
    half = road_w / 2
    ax.plot([stop_s, stop_s], [-half, 0],
            color=STOP_LINE, lw=3.5, zorder=3)
    ax.plot([-stop_s, -stop_s], [0, half],
            color=STOP_LINE, lw=3.5, zorder=3)
    ax.plot([0, half], [stop_s, stop_s],
            color=STOP_LINE, lw=3.5, zorder=3)
    ax.plot([-half, 0], [-stop_s, -stop_s],
            color=STOP_LINE, lw=3.5, zorder=3)
    draw_flow_arrows(ax)


def car_rect(ax, x, y, orientation, color, w=8, l=14):
    if orientation == "h":
        ax.add_patch(Rectangle((x - l / 2, y - w / 2), l, w,
                               facecolor=color, edgecolor="black", lw=0.8, zorder=4))
    else:
        ax.add_patch(Rectangle((x - w / 2, y - l / 2), w, l,
                               facecolor=color, edgecolor="black", lw=0.8, zorder=4))


def draw_signal(ax, h_red, v_red):
    ax.add_patch(Rectangle((-22, -22), 44, 44, facecolor="#222",
                           edgecolor="black", lw=1.2, zorder=5))
    ax.add_patch(plt.Circle((-10, 0), 6,
                            facecolor=("#e74c3c" if h_red else "#2ecc71"),
                            edgecolor="black", lw=0.8, zorder=6))
    ax.add_patch(plt.Circle((10, 0), 6,
                            facecolor=("#e74c3c" if v_red else "#2ecc71"),
                            edgecolor="black", lw=0.8, zorder=6))
    ax.text(-10, -16, "H", color="white", ha="center", fontsize=8, zorder=6)
    ax.text(10, -16, "V", color="white", ha="center", fontsize=8, zorder=6)


def main():
    random.seed(7)
    dt = 0.01
    T = 90.0
    period = 20.0
    n = int(T / dt)
    lane_off = 6.0

    sig_h = Signal(loc=LIGHT_STOP_LINE, period=period, offset=0.0)
    sig_v = Signal(loc=LIGHT_STOP_LINE, period=period, offset=period / 2)
    lane_e = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_w = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_n = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)
    lane_s = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)

    snaps_e, snaps_w, snaps_n, snaps_s, ts = [], [], [], [], []
    for i in range(n):
        t = i * dt
        lane_e.try_spawn(t, dt, rate=0.4)
        lane_w.try_spawn(t, dt, rate=0.4)
        lane_n.try_spawn(t, dt, rate=0.4)
        lane_s.try_spawn(t, dt, rate=0.4)
        for ln in (lane_e, lane_w, lane_n, lane_s):
            ln.step(t, dt)
        if i % 30 == 0:
            ts.append(t)
            snaps_e.append(lane_e.positions)
            snaps_w.append(lane_w.positions)
            snaps_n.append(lane_n.positions)
            snaps_s.append(lane_s.positions)

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    ax.set_xlim(-230, 230)
    ax.set_ylim(-230, 230)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    draw_intersection(ax)

    snap_idx = -1
    t_show = ts[snap_idx]
    for s in snaps_e[snap_idx]:
        car_rect(ax, s, -lane_off, "h", "#1f3a93")
    for s in snaps_w[snap_idx]:
        car_rect(ax, -s, lane_off, "h", "#2e86c1")
    for s in snaps_n[snap_idx]:
        car_rect(ax, lane_off, s, "v", "#e67e22")
    for s in snaps_s[snap_idx]:
        car_rect(ax, -lane_off, -s, "v", "#d35400")

    h_red = sig_h.red(t_show)
    v_red = sig_v.red(t_show)
    draw_signal(ax, h_red, v_red)

    ax.set_title(f"Crossroads with opposing-phase traffic lights "
                 f"(t = {t_show:.0f} s, H={'R' if h_red else 'G'}, V={'R' if v_red else 'G'})",
                 fontsize=12)
    plt.tight_layout()
    plt.savefig("../figures/fig_step3_intersection_lights.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
