import matplotlib.pyplot as plt
import numpy as np

from sim_core import run_lights


def main():
    rates_h = np.array([0.10, 0.20, 0.30, 0.40, 0.50, 0.60])
    rates_v = np.array([0.10, 0.20, 0.30, 0.40, 0.50, 0.60])
    diff = np.zeros((len(rates_h), len(rates_v)))

    print(f"Lights H-V difference sweep: {len(rates_h)} x {len(rates_v)} grid")
    for i, rh in enumerate(rates_h):
        for j, rv in enumerate(rates_v):
            th, tv, T = run_lights(rate_h=rh, rate_v=rv, T=200.0, period=20.0, seed=81)
            mh = float(np.mean(th)) if th else float("nan")
            mv = float(np.mean(tv)) if tv else float("nan")
            diff[i, j] = mh - mv
            print(f"  rate_h={rh:.2f}  rate_v={rv:.2f}  H={mh:6.2f}  V={mv:6.2f}  H-V={diff[i,j]:+6.2f}")

    fig, ax = plt.subplots(figsize=(7.5, 6))
    vmax = float(np.nanmax(np.abs(diff)))
    if vmax < 1e-3:
        vmax = 1.0
    extent = [rates_v.min() - 0.05, rates_v.max() + 0.05,
              rates_h.min() - 0.05, rates_h.max() + 0.05]
    im = ax.imshow(diff, origin="lower", extent=extent, aspect="auto",
                   cmap="seismic", vmin=-vmax, vmax=vmax, interpolation="bilinear")
    cs = ax.contour(rates_v, rates_h, diff, levels=[0], colors="black", linewidths=1.5)
    ax.clabel(cs, inline=True, fontsize=9, fmt="%.0f")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(r"$\langle t \rangle_H - \langle t \rangle_V$  (s)")
    ax.set_xlabel("vertical spawn rate (cars / s)")
    ax.set_ylabel("horizontal spawn rate (cars / s)")
    ax.set_title("Traffic light: H − V passing-time difference")
    ax.plot(rates_v, rates_h, color="black", ls=":", label="symmetric line")
    ax.legend()
    plt.tight_layout()
    plt.savefig("../figures/fig_analysis8_lights_hv_difference.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
