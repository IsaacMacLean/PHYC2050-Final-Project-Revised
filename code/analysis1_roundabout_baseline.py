import matplotlib.pyplot as plt
import numpy as np

from round_core import run_roundabout


def main():
    rate = 0.3
    times_h, times_v, T = run_roundabout(rate_h=rate, rate_v=rate, T=300.0,
                                         dt=0.05, seed=11)

    mh = float(np.mean(times_h)) if times_h else float("nan")
    mv = float(np.mean(times_v)) if times_v else float("nan")
    all_t = times_h + times_v
    m_all = float(np.mean(all_t)) if all_t else float("nan")

    print(f"Horizontal: N={len(times_h):4d}  mean passing time = {mh:6.2f} s")
    print(f"Vertical:   N={len(times_v):4d}  mean passing time = {mv:6.2f} s")
    print(f"Combined:   N={len(all_t):4d}  mean passing time = {m_all:6.2f} s")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bins = np.linspace(0, max(all_t) * 1.05 if all_t else 100, 30)
    ax.hist(times_h, bins=bins, color="navy", alpha=0.55,
            label=f"horizontal  (mean = {mh:.1f} s)")
    ax.hist(times_v, bins=bins, color="darkorange", alpha=0.55,
            label=f"vertical    (mean = {mv:.1f} s)")
    ax.axvline(mh, color="navy", ls="--", lw=1)
    ax.axvline(mv, color="darkorange", ls="--", lw=1)
    ax.set_xlabel("passing time (s)")
    ax.set_ylabel("number of cars")
    ax.set_title(f"Roundabout passing-time distribution "
                 f"(spawn = {rate} cars/s/road, T = {T:.0f} s)")
    ax.legend()
    ax.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig("../figures/fig_analysis1_roundabout_baseline.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
