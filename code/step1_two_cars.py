import matplotlib.pyplot as plt

from sim_core import Vehicle, integrate


def schedule(t, leader):
    leader.v_target = 0.0 if 10.0 <= t < 30.0 else 15.0


def main():
    leader = Vehicle(s=50.0, vel=15.0)
    follower = Vehicle(s=0.0, vel=15.0)

    dt = 0.01
    T = 60.0
    n = int(T / dt)

    times, s_l, s_f, v_l, v_f, gap = [], [], [], [], [], []
    for i in range(n):
        t = i * dt
        schedule(t, leader)
        integrate(leader, dt, blocker_s=None)
        integrate(follower, dt, blocker_s=leader.s)
        times.append(t)
        s_l.append(leader.s)
        s_f.append(follower.s)
        v_l.append(leader.vel)
        v_f.append(follower.vel)
        gap.append(leader.s - follower.s)

    fig, axes = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    axes[0].plot(times, s_l, color="firebrick", label="leader")
    axes[0].plot(times, s_f, color="steelblue", label="follower")
    axes[0].set_ylabel("arc length s (m)")
    axes[0].legend()

    axes[1].plot(times, v_l, color="firebrick", label="leader")
    axes[1].plot(times, v_f, color="steelblue", label="follower")
    axes[1].set_ylabel("velocity (m/s)")
    axes[1].legend()

    axes[2].plot(times, gap, color="black")
    axes[2].axhline(15.0, ls="--", color="gray", label=r"$\sigma$")
    axes[2].set_xlabel("time (s)")
    axes[2].set_ylabel("gap (m)")
    axes[2].legend()

    fig.suptitle("Two-vehicle Lennard-Jones car-following test")
    plt.tight_layout()
    plt.savefig("../figures/fig_step1_two_vehicles.png", dpi=150, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
