import random
from dataclasses import dataclass


CAR_LENGTH = 14.0
FOLLOW_GAP = 4.0
SPAWN_GAP = CAR_LENGTH + FOLLOW_GAP + 2.0
LIGHT_STOP_LINE = -30.0


@dataclass
class Vehicle:
    s: float
    vel: float = 0.0
    v_target: float = 11.0
    relax: float = 2.0
    sigma: float = 7.0
    length: float = CAR_LENGTH
    born: float = 0.0


def lj_brake(sigma, gap, vel):
    g = gap if gap > 0.5 else 0.5
    return -((sigma / g) ** 12) * vel


def integrate(veh, dt, blocker_s):
    drive = (veh.v_target - veh.vel) / veh.relax
    brake = 0.0 if blocker_s is None else lj_brake(veh.sigma, blocker_s - veh.s, veh.vel)
    veh.vel = max(0.0, veh.vel + (drive + brake) * dt)
    veh.s += veh.vel * dt


def integrate_gap(veh, dt, blocker_gap):
    drive = (veh.v_target - veh.vel) / veh.relax
    brake = 0.0 if blocker_gap is None else lj_brake(veh.sigma, blocker_gap, veh.vel)
    veh.vel = max(0.0, veh.vel + (drive + brake) * dt)
    veh.s += veh.vel * dt


@dataclass
class Signal:
    loc: float
    period: float = 10.0
    offset: float = 0.0

    def red(self, t):
        return ((t + self.offset) % self.period) < (self.period / 2)


class StopBlocker:
    def __init__(self, loc):
        self.loc = loc

    def red(self, t):
        return True


class OpenBlocker:
    def __init__(self, loc):
        self.loc = loc

    def red(self, t):
        return False


class Lane:
    def __init__(self, signal=None, entry_s=-95.0, exit_s=65.0,
                 min_gap=SPAWN_GAP, follow_gap=FOLLOW_GAP):
        self.signal = signal
        self.entry_s = entry_s
        self.exit_s = exit_s
        self.min_gap = min_gap
        self.follow_gap = follow_gap
        self.queue = []
        self.passing_times = []

    def step(self, t, dt):
        for idx, veh in enumerate(self.queue):
            blocker_gap = None
            max_s = None

            if idx > 0:
                leader = self.queue[idx - 1]
                blocker_gap = leader.s - veh.s - veh.length
                max_s = leader.s - veh.length - self.follow_gap

            if (self.signal is not None and self.signal.red(t)
                    and veh.s + veh.length / 2 < self.signal.loc):
                light_gap = self.signal.loc - (veh.s + veh.length / 2)
                if blocker_gap is None or light_gap < blocker_gap:
                    blocker_gap = light_gap
                    max_s = self.signal.loc - veh.length / 2

            integrate_gap(veh, dt, blocker_gap)
            if max_s is not None and veh.s > max_s:
                veh.s = max_s
                veh.vel = 0.0

        while self.queue and self.queue[0].s > self.exit_s:
            v = self.queue.pop(0)
            self.passing_times.append(t - v.born)

    def try_spawn(self, t, dt, rate):
        if random.random() >= rate * dt:
            return False
        if self.queue and self.queue[-1].s < self.entry_s + self.min_gap:
            return False
        self.queue.append(Vehicle(s=self.entry_s, vel=10.0, born=t))
        return True

    @property
    def positions(self):
        return [v.s for v in self.queue]


def run_lights(rate_h, rate_v, T=300.0, dt=0.05, period=20.0,
               entry_s=-95.0, exit_s=65.0, seed=0):
    random.seed(seed)
    sig_h = Signal(loc=LIGHT_STOP_LINE, period=period, offset=0.0)
    sig_v = Signal(loc=LIGHT_STOP_LINE, period=period, offset=period / 2)
    lane_h = Lane(signal=sig_h, entry_s=entry_s, exit_s=exit_s)
    lane_v = Lane(signal=sig_v, entry_s=entry_s, exit_s=exit_s)
    n_steps = int(T / dt)
    for i in range(n_steps):
        t = i * dt
        lane_h.try_spawn(t, dt, rate_h)
        lane_v.try_spawn(t, dt, rate_v)
        lane_h.step(t, dt)
        lane_v.step(t, dt)
    return lane_h.passing_times, lane_v.passing_times, T
