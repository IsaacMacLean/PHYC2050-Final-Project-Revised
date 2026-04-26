import matplotlib.pyplot as plt
import numpy as np

from sim_core import run_lights


def main():
    rates = np.array([0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80])
    means_density = []
    print(f"Density sweep (period = 20 s):")
    print(f"{'rate':>6}  {'<t>':>7}  {'N':>5}")
    for r in rates:
        th, tv, T = run_lights(rate_h=r, rate_v=r, T=300.0, period=20.0, seed=51)
        all_t = th + tv
        m = float(np.mean(all_t)) if all_t else float("nan")
        means_density.append(m)
        print(f"{r:6.2f}  {m:7.2f}  {len(all_t):5d}")

    cycles = np.array([5, 10, 15, 20, 25, 30, 40, 50, 60, 80], dtype=float)
    means_cycle = []
    fixed_rate = 0.4
    print(f"\nCycle sweep (rate = {fixed_rate} cars/s/road):")
    print(f"{'cycle':>6}  {'<t>':>7}  {'N':>5}")
    for c in cycles:
        th, tv, T = run_lights(rate_h=fixed_rate, rate_v=fixed_rate, T=300.0,
                               period=c, seed=52)
        all_t = th + tv
        m = float(np.mean(all_t)) if all_t else float("nan")
        means_cycle.append(m)
        print(f"{c:6.1f}  {m:7.2f}  {len(all_t):5d}")

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
    ax[0].plot(rates, means_density, marker="o", color="forestgreen")
    ax[0].set_xlabel("spawn rate per road (cars / s)")
    ax[0].set_ylabel("mean passing time (s)")
    ax[0].set_title("Traffic light: passing time vs density (20 s cycle)")
    ax[0].grid(alpha=0.3)

    ax[1].plot(cycles, means_cycle, marker="^", color="forestgreen")
    ax[1].set_xlabel("cycle period (s)")
    ax[1].set_ylabel("mean passing time (s)")
    ax[1].set_title(f"Traffic light: passing time vs cycle (rate = {fixed_rate})")
    ax[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("../figures/fig_analysis5_lights_density_and_cycle.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
