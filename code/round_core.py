import math
import numpy as np
from dataclasses import dataclass, field

TWOPI = 2.0 * math.pi
ARM_COLORS = ["#1f77b4", "#2ca02c", "#d62728", "#9467bd"]


@dataclass
class Vehicle:
    car_id: int
    arm: int
    exit_arm: int
    born: float
    r: float
    theta: float
    vel: float = 0.0
    state: str = "approach"
    color: str = "#1f77b4"
    sigma: float = 7.0
    relax: float = 2.0
    car_length: float = 4.5
    entry_time: float = -1.0
    exit_ring_time: float = -1.0
    finish_time: float = -1.0


def lj_brake_acc(sigma, gap, vel):
    g = gap if gap > 0.5 else 0.5
    return -((sigma / g) ** 12) * vel


def relax_step(veh, dt, blocker_gap, vmax):
    drive = (vmax - veh.vel) / veh.relax
    brake = 0.0 if blocker_gap is None else lj_brake_acc(veh.sigma, blocker_gap, veh.vel)
    veh.vel = max(0.0, veh.vel + (drive + brake) * dt)


def arm_angle(arm):
    return (arm % 4) * (math.pi / 2)


def passed_target(old_theta, new_theta, target):
    travelled = (new_theta - old_theta) % TWOPI
    needed = (target - old_theta) % TWOPI
    return needed <= travelled and travelled > 1e-9


def _can_enter_ring(car, ring_cars, radius, min_gap, reaction_time, capacity_gap):
    if not ring_cars:
        return True
    max_capacity = max(1, int((TWOPI * radius) // capacity_gap))
    if len(ring_cars) >= max_capacity:
        return False
    entry = arm_angle(car.arm)
    speed_scale = max([car.vel] + [c.vel for c in ring_cars])
    yield_gap = max(min_gap, reaction_time * speed_scale)
    follow_gap = max(min_gap, car.car_length + 2.0)
    for other in ring_cars:
        ccw_dist = radius * ((entry - other.theta) % TWOPI)
        ahead_dist = radius * ((other.theta - entry) % TWOPI)
        if 0.0 < ccw_dist < yield_gap:
            return False
        if 0.0 < ahead_dist < follow_gap:
            return False
    return True


def _update_approach(cars, t, dt, radius, road_vmax, ring_vmax,
                     min_gap, reaction_time, stop_buffer, capacity_gap):
    stop_r = radius + stop_buffer
    ring_cars = [c for c in cars if c.state == "circle"]
    for arm in range(4):
        approaching = sorted(
            (c for c in cars if c.state == "approach" and c.arm == arm),
            key=lambda c: c.r,
        )
        for i, car in enumerate(approaching):
            if i == 0:
                allowed = _can_enter_ring(car, ring_cars, radius,
                                          min_gap, reaction_time, capacity_gap)
                blocked = car.r <= stop_r + 0.25 and not allowed
                gap = 0.1 if blocked else None
            else:
                front = approaching[i - 1]
                gap = car.r - front.r - car.car_length
            speed_limit = min(road_vmax,
                              ring_vmax * 1.4 if car.r < radius + 18.0 else road_vmax)
            relax_step(car, dt, gap, speed_limit)
            car.r -= car.vel * dt
            if car.r <= stop_r:
                if _can_enter_ring(car, ring_cars, radius,
                                   min_gap, reaction_time, capacity_gap):
                    car.state = "circle"
                    car.r = radius
                    car.theta = arm_angle(car.arm)
                    car.vel = max(0.6, min(car.vel, ring_vmax))
                    car.entry_time = t
                    ring_cars.append(car)
                else:
                    car.r = stop_r
                    car.vel = 0.0


def _update_circle(cars, t, dt, radius, ring_vmax, follow_gap_min):
    ring_cars = [c for c in cars if c.state == "circle"]
    if not ring_cars:
        return
    ring_cars.sort(key=lambda c: c.theta % TWOPI)
    n = len(ring_cars)
    for i, car in enumerate(ring_cars):
        if n == 1:
            gap = None
        else:
            front = ring_cars[(i + 1) % n]
            gap = max(0.0, radius * ((front.theta - car.theta) % TWOPI) - car.car_length)
        relax_step(car, dt, gap, ring_vmax)
        if gap is not None and gap < follow_gap_min:
            car.vel = max(0.0, car.vel + lj_brake_acc(car.sigma, max(gap, 0.5), car.vel) * dt)
    for car in list(ring_cars):
        old_theta = car.theta % TWOPI
        car.theta = (car.theta + car.vel * dt / radius) % TWOPI
        target = arm_angle(car.exit_arm)
        if passed_target(old_theta, car.theta, target):
            car.state = "exit"
            car.r = radius
            car.theta = target
            car.exit_ring_time = t


def _update_exits(cars, t, dt, road_vmax, finish_r):
    for exit_arm in range(4):
        exiting = sorted(
            (c for c in cars if c.state == "exit" and c.exit_arm == exit_arm),
            key=lambda c: -c.r,
        )
        for i, car in enumerate(exiting):
            gap = None if i == 0 else exiting[i - 1].r - car.r - car.car_length
            relax_step(car, dt, gap, road_vmax)
            car.r += car.vel * dt
            if car.r >= finish_r:
                car.state = "done"
                car.finish_time = t


def _can_spawn(cars, arm, spawn_r, min_spawn_gap):
    same = [c for c in cars if c.state == "approach" and c.arm == arm]
    if not same:
        return True
    return max(c.r for c in same) < spawn_r - min_spawn_gap


def run_roundabout_sim(rate_h=0.08, rate_v=0.08, opposite=False, spawn_rates=None,
                      T=220.0, dt=0.1, seed=0,
                      radius=15.0, road_length=95.0, exit_length=35.0,
                      road_vmax=11.0, ring_vmax=5.5,
                      min_gap=8.0, reaction_time=1.2,
                      follow_gap_min=7.5, capacity_gap=7.0,
                      min_spawn_gap=10.0,
                      record=False, record_stride=5,
                      warmup=50.0):
    rng = np.random.default_rng(seed)
    if spawn_rates is None:
        if opposite:
            spawn_rates = [rate_h, rate_v, rate_h, rate_v]
        else:
            spawn_rates = [0.0, 0.0, rate_h, rate_v]
    spawn_rates = np.asarray(spawn_rates, dtype=float)

    finish_r = radius + exit_length
    cars = []
    frames = []
    next_id = 0
    n_steps = int(math.ceil(T / dt))

    for step in range(n_steps):
        t = step * dt
        for arm, rate in enumerate(spawn_rates):
            arrivals = int(rng.poisson(rate * dt))
            for _ in range(arrivals):
                if _can_spawn(cars, arm, road_length, min_spawn_gap):
                    exit_arm = (arm + 2) % 4
                    cars.append(Vehicle(
                        car_id=next_id, arm=arm, exit_arm=exit_arm,
                        born=t, r=road_length, theta=arm_angle(arm),
                        vel=road_vmax * 0.65,
                        color=ARM_COLORS[arm],
                    ))
                    next_id += 1
        _update_approach(cars, t, dt, radius, road_vmax, ring_vmax,
                         min_gap, reaction_time, stop_buffer=2.0, capacity_gap=capacity_gap)
        _update_circle(cars, t, dt, radius, ring_vmax, follow_gap_min)
        _update_exits(cars, t, dt, road_vmax, finish_r)
        if record and step % record_stride == 0:
            frames.append(_snapshot(cars, t))

    return _summarize(cars, T, warmup, radius, road_length, finish_r, spawn_rates, frames)


def _snapshot(cars, t):
    items = []
    for c in cars:
        if c.state == "done":
            continue
        x = c.r * math.cos(c.theta)
        y = c.r * math.sin(c.theta)
        items.append({
            "x": x, "y": y, "theta": c.theta,
            "color": c.color, "arm": c.arm, "state": c.state,
        })
    return {"time": t, "cars": items}


def _summarize(cars, T, warmup, radius, road_length, finish_r, spawn_rates, frames):
    finished = [c for c in cars if c.finish_time >= 0]
    measured = [c for c in finished if c.finish_time >= warmup and c.born >= warmup]
    if len(measured) < 3:
        measured = finished
    times_h, times_v = [], []
    for c in measured:
        total = c.finish_time - c.born
        if c.arm in (0, 2):
            times_h.append(total)
        else:
            times_v.append(total)
    flow_meas_T = max(T - warmup, 1e-9)
    n_finished_warm = sum(1 for c in finished if c.finish_time >= warmup)
    return {
        "times_h": times_h,
        "times_v": times_v,
        "T": T,
        "warmup": warmup,
        "radius": radius,
        "road_length": road_length,
        "finish_r": finish_r,
        "spawn_rates": spawn_rates,
        "frames": frames,
        "n_cars": len(cars),
        "n_finished": len(finished),
        "n_measured": len(measured),
        "flow": n_finished_warm / flow_meas_T,
    }


def run_roundabout(rate_h, rate_v, T=220.0, dt=0.1, seed=0, opposite=False, **kw):
    out = run_roundabout_sim(rate_h=rate_h, rate_v=rate_v, T=T, dt=dt,
                             seed=seed, opposite=opposite, **kw)
    return out["times_h"], out["times_v"], out["T"]
