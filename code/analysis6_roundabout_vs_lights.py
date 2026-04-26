import matplotlib.pyplot as plt
import numpy as np

from round_core import run_roundabout
from sim_core import run_lights


def main():
    rates = np.array([0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80])
    means_round = []
    means_lights = []

    print(f"{'rate':>6}  {'<t>_round':>10}  {'<t>_lights':>11}")
    for r in rates:
        th_r, tv_r, T = run_roundabout(rate_h=r, rate_v=r, T=200.0, dt=0.05, seed=61)
        th_l, tv_l, _ = run_lights(rate_h=r, rate_v=r, T=200.0, period=20.0, seed=62)
        m_r = float(np.mean(th_r + tv_r)) if (th_r or tv_r) else float("nan")
        m_l = float(np.mean(th_l + tv_l)) if (th_l or tv_l) else float("nan")
        means_round.append(m_r)
        means_lights.append(m_l)
        print(f"{r:6.2f}  {m_r:10.2f}  {m_l:11.2f}")

    means_round = np.array(means_round)
    means_lights = np.array(means_lights)

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
    ax[0].plot(rates, means_round, marker="D", color="firebrick", label="roundabout")
    ax[0].plot(rates, means_lights, marker="o", color="forestgreen", label="traffic light")
    ax[0].set_xlabel("spawn rate per road (cars / s)")
    ax[0].set_ylabel("mean passing time (s)")
    ax[0].set_title("Mean passing time: roundabout vs traffic light")
    ax[0].legend()
    ax[0].grid(alpha=0.3)

    diff = means_lights - means_round
    ax[1].bar(rates, diff, width=0.04,
              color=np.where(diff > 0, "firebrick", "forestgreen"),
              edgecolor="black", alpha=0.8)
    ax[1].axhline(0, color="black", lw=0.8)
    ax[1].set_xlabel("spawn rate per road (cars / s)")
    ax[1].set_ylabel(r"$\langle t \rangle_{lights} - \langle t \rangle_{round}$  (s)")
    ax[1].set_title("Where each control wins (positive = roundabout faster)")
    ax[1].grid(alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig("../figures/fig_analysis6_roundabout_vs_lights.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
