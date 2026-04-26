import matplotlib.pyplot as plt
import numpy as np

from round_core import run_roundabout
from sim_core import run_lights


def main():
    rates = np.array([0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80])
    flow_round = []
    flow_lights = []

    print(f"{'rate':>6}  {'flow_round':>10}  {'flow_lights':>11}")
    for r in rates:
        th_r, tv_r, T = run_roundabout(rate_h=r, rate_v=r, T=200.0, dt=0.05, seed=91)
        th_l, tv_l, _ = run_lights(rate_h=r, rate_v=r, T=200.0, period=20.0, seed=92)
        fr = (len(th_r) + len(tv_r)) / T
        fl = (len(th_l) + len(tv_l)) / T
        flow_round.append(fr)
        flow_lights.append(fl)
        print(f"{r:6.2f}  {fr:10.3f}  {fl:11.3f}")

    flow_round = np.array(flow_round)
    flow_lights = np.array(flow_lights)

    fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))

    ax[0].plot(rates, flow_round, marker="D", color="firebrick", label="roundabout")
    ax[0].plot(rates, flow_lights, marker="o", color="forestgreen", label="traffic light")
    ax[0].plot(rates, 2 * rates, color="gray", ls="--", alpha=0.6,
               label="2 × spawn (no losses)")
    ax[0].set_xlabel("spawn rate per road (cars / s)")
    ax[0].set_ylabel("total exit flow (cars / s)")
    ax[0].set_title("Throughput: roundabout vs traffic light")
    ax[0].legend()
    ax[0].grid(alpha=0.3)

    saturation = np.where(2 * rates > 0, flow_round / (2 * rates), 0)
    sat_l = np.where(2 * rates > 0, flow_lights / (2 * rates), 0)
    ax[1].plot(rates, saturation, marker="D", color="firebrick", label="roundabout")
    ax[1].plot(rates, sat_l, marker="o", color="forestgreen", label="traffic light")
    ax[1].axhline(1.0, color="gray", ls="--", alpha=0.6, label="100 % efficiency")
    ax[1].set_xlabel("spawn rate per road (cars / s)")
    ax[1].set_ylabel("exit flow / spawn flow")
    ax[1].set_title("Throughput efficiency")
    ax[1].set_ylim(0, 1.15)
    ax[1].legend()
    ax[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("../figures/fig_analysis9_flow_rate_comparison.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
