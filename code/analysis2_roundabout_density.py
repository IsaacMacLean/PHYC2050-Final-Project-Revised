import matplotlib.pyplot as plt
import numpy as np

from round_core import run_roundabout


def main():
    rates = np.array([0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80])
    means, throughputs = [], []
    print(f"{'rate':>6}  {'<t>':>7}  {'flow':>7}  {'N':>5}")
    for r in rates:
        th, tv, T = run_roundabout(rate_h=r, rate_v=r, T=200.0, dt=0.05, seed=21)
        all_t = th + tv
        m = float(np.mean(all_t)) if all_t else float("nan")
        flow = len(all_t) / T
        means.append(m)
        throughputs.append(flow)
        print(f"{r:6.2f}  {m:7.2f}  {flow:7.3f}  {len(all_t):5d}")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    ax[0].plot(rates, means, marker="D", color="firebrick")
    ax[0].set_xlabel("spawn rate per road (cars / s)")
    ax[0].set_ylabel("mean passing time (s)")
    ax[0].set_title("Roundabout: passing time vs density")
    ax[0].grid(alpha=0.3)

    ax[1].plot(rates, throughputs, marker="D", color="firebrick", label="exit flow")
    ax[1].plot(rates, 2 * rates, color="gray", ls="--", label="2 × spawn (no losses)")
    ax[1].set_xlabel("spawn rate per road (cars / s)")
    ax[1].set_ylabel("total exit flow (cars / s)")
    ax[1].set_title("Roundabout: throughput")
    ax[1].grid(alpha=0.3)
    ax[1].legend()

    plt.tight_layout()
    plt.savefig("../figures/fig_analysis2_roundabout_density.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
