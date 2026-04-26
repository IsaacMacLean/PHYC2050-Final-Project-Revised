import matplotlib.pyplot as plt

from sim_core import Lane, Signal, Vehicle


def main():
    dt = 0.01
    T = 60.0
    n = int(T / dt)

    sig = Signal(loc=0.0, period=20.0, offset=0.0)
    lane = Lane(signal=sig, entry_s=-200.0, exit_s=300.0)

    N = 8
    for i in range(N):
        lane.queue.append(Vehicle(s=-200.0 + i * 20.0, vel=10.0, born=0.0))
    lane.queue.reverse()

    times, frames = [], []
    for i in range(n):
        t = i * dt
        lane.step(t, dt)
        if i % 5 == 0:
            times.append(t)
            frames.append([v.s for v in lane.queue])

    max_track = max(len(fr) for fr in frames)
    tracks = [[] for _ in range(max_track)]
    track_t = [[] for _ in range(max_track)]
    for fi, fr in enumerate(frames):
        for k, s in enumerate(fr):
            tracks[k].append(s)
            track_t[k].append(times[fi])

    fig, axes = plt.subplots(2, 1, figsize=(11, 6))
    for k in range(len(tracks)):
        axes[0].plot(track_t[k], tracks[k], lw=0.9)
    axes[0].axhline(sig.loc, color="red", ls="--", alpha=0.6, label="stop line")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("position (m)")
    axes[0].set_title("Fleet trajectories through a pedestrian light (period 20 s)")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    snap = frames[-1]
    axes[1].set_xlim(-220, 320)
    axes[1].set_ylim(-1, 1)
    axes[1].set_yticks([])
    axes[1].axhline(0, color="lightgray", lw=8, zorder=0)
    axes[1].plot(snap, [0] * len(snap), marker="s", linestyle="",
                 markersize=12, color="midnightblue")
    is_red = sig.red(times[-1])
    axes[1].plot([sig.loc], [0], marker="o", markersize=18,
                 color=("crimson" if is_red else "limegreen"))
    axes[1].set_xlabel("position (m)")
    axes[1].set_title(f"Snapshot at t = {times[-1]:.1f} s, light = {'red' if is_red else 'green'}")

    plt.tight_layout()
    plt.savefig("../figures/fig_step2_pedestrian_light.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
