import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, FFMpegWriter

from sim_core import Lane, LIGHT_STOP_LINE, Signal
from step3_intersection_lights import draw_intersection


def main():
    random.seed(7)
    dt = 0.05
    T = 80.0
    period = 20.0
    n = int(T / dt)
    lane_off = 6.0
    record_every = 4
    spawn_rate = 0.25

    sig_h = Signal(loc=LIGHT_STOP_LINE, period=period, offset=0.0)
    sig_v = Signal(loc=LIGHT_STOP_LINE, period=period, offset=period / 2)
    lane_e = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_w = Lane(signal=sig_h, entry_s=-200.0, exit_s=200.0)
    lane_n = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)
    lane_s = Lane(signal=sig_v, entry_s=-200.0, exit_s=200.0)

    snaps = []
    for i in range(n):
        t = i * dt
        for ln in (lane_e, lane_w, lane_n, lane_s):
            ln.try_spawn(t, dt, rate=spawn_rate)
            ln.step(t, dt)
        if i % record_every == 0:
            snaps.append({
                "t": t,
                "e": list(lane_e.positions),
                "w": list(lane_w.positions),
                "n": list(lane_n.positions),
                "s": list(lane_s.positions),
                "h_red": sig_h.red(t),
                "v_red": sig_v.red(t),
            })

    fig = plt.figure(figsize=(8, 8), dpi=120)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-230, 230); ax.set_ylim(-230, 230)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    draw_intersection(ax)

    sc_e = ax.scatter([], [], marker="s", s=180, c="#1f3a93",
                      edgecolor="black", lw=0.6, zorder=4)
    sc_w = ax.scatter([], [], marker="s", s=180, c="#2e86c1",
                      edgecolor="black", lw=0.6, zorder=4)
    sc_n = ax.scatter([], [], marker="s", s=180, c="#e67e22",
                      edgecolor="black", lw=0.6, zorder=4)
    sc_s = ax.scatter([], [], marker="s", s=180, c="#d35400",
                      edgecolor="black", lw=0.6, zorder=4)

    from matplotlib.patches import Rectangle, Circle
    sig_box = Rectangle((-22, -22), 44, 44, facecolor="#222",
                        edgecolor="black", lw=1.2, zorder=5)
    ax.add_patch(sig_box)
    h_circ = Circle((-10, 0), 6, facecolor="#e74c3c",
                    edgecolor="black", lw=0.8, zorder=6)
    v_circ = Circle((10, 0), 6, facecolor="#2ecc71",
                    edgecolor="black", lw=0.8, zorder=6)
    ax.add_patch(h_circ); ax.add_patch(v_circ)
    ax.text(-10, -16, "H", color="white", ha="center", fontsize=8, zorder=6)
    ax.text(10, -16, "V", color="white", ha="center", fontsize=8, zorder=6)

    title = ax.text(0.5, 0.97, "", transform=ax.transAxes,
                    ha="center", va="top", fontsize=12,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.85))

    def to_offsets(s_list, axis, sign):
        if not s_list:
            return np.empty((0, 2))
        if axis == "h":
            return np.array([[sign * s, -lane_off if sign > 0 else lane_off] for s in s_list])
        else:
            return np.array([[lane_off if sign > 0 else -lane_off, sign * s] for s in s_list])

    def update(idx):
        snap = snaps[idx]
        sc_e.set_offsets(to_offsets(snap["e"], "h", +1))
        sc_w.set_offsets(to_offsets(snap["w"], "h", -1))
        sc_n.set_offsets(to_offsets(snap["n"], "v", +1))
        sc_s.set_offsets(to_offsets(snap["s"], "v", -1))
        h_circ.set_facecolor("#e74c3c" if snap["h_red"] else "#2ecc71")
        v_circ.set_facecolor("#e74c3c" if snap["v_red"] else "#2ecc71")
        title.set_text(f"Crossroads with traffic lights "
                       f"(t = {snap['t']:.0f} s, "
                       f"H={'R' if snap['h_red'] else 'G'}, "
                       f"V={'R' if snap['v_red'] else 'G'})")
        return sc_e, sc_w, sc_n, sc_s, h_circ, v_circ, title

    anim = FuncAnimation(fig, update, frames=len(snaps), interval=50, blit=False)
    writer = FFMpegWriter(fps=20, bitrate=2400,
                          extra_args=["-pix_fmt", "yuv420p"])
    anim.save("../animations/lights.mp4", writer=writer, dpi=120,
              savefig_kwargs={"facecolor": "white"})
    plt.close(fig)


if __name__ == "__main__":
    main()
