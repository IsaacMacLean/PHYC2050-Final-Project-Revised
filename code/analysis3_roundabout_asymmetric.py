import matplotlib.pyplot as plt
import numpy as np

from round_core import run_roundabout


def main():
    rates_h = np.array([0.10, 0.20, 0.30, 0.40, 0.50, 0.60])
    rates_v = np.array([0.10, 0.20, 0.30, 0.40, 0.50, 0.60])
    grid = np.zeros((len(rates_h), len(rates_v)))

    print(f"Asymmetric sweep: {len(rates_h)} x {len(rates_v)} grid")
    for i, rh in enumerate(rates_h):
        for j, rv in enumerate(rates_v):
            th, tv, T = run_roundabout(rate_h=rh, rate_v=rv, T=150.0, dt=0.05, seed=31)
            all_t = th + tv
            grid[i, j] = float(np.mean(all_t)) if all_t else float("nan")
            print(f"  rate_h={rh:.2f}  rate_v={rv:.2f}  <t>={grid[i,j]:6.2f} s  N={len(all_t)}")

    fig, ax = plt.subplots(figsize=(7.5, 6))
    extent = [rates_v.min() - 0.05, rates_v.max() + 0.05,
              rates_h.min() - 0.05, rates_h.max() + 0.05]
    im = ax.imshow(grid, origin="lower", extent=extent, aspect="auto",
                   cmap="magma", interpolation="bilinear")
    cs = ax.contour(rates_v, rates_h, grid, levels=8, colors="white", linewidths=0.7)
    ax.clabel(cs, inline=True, fontsize=8, fmt="%.0f")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("mean passing time (s)")
    ax.set_xlabel("vertical spawn rate (cars / s)")
    ax.set_ylabel("horizontal spawn rate (cars / s)")
    ax.set_title("Roundabout: mean passing time vs asymmetric spawn rates")
    ax.plot(rates_v, rates_h, color="cyan", ls=":", label="symmetric line")
    ax.legend()
    plt.tight_layout()
    plt.savefig("../figures/fig_analysis3_roundabout_asymmetric.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
