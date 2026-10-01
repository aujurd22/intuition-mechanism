"""SDB domain 1: scientific data — damped oscillation with a hidden
anomaly class (P148).

Hidden structure S (not named in the charter):
  x(t) = A * exp(-gamma*t) * sin(2*pi*t/T)
  plus an ANOMALY class: series where the sign of every other extremum
  is flipped (a phase inversion the tests do not mention).

Discovery = recover (T, gamma) from raw samples and detect the phase-
inversion class.  Transfer = a different (T, gamma, A) regime.
"""
import math
import random


def gen_series(T, gamma, A=1.0, n=40, dt=0.25, anomaly=False, rng=None):
    """Damped oscillation sampled at t = 0..(n-1)*dt."""
    xs = []
    for i in range(n):
        t = i * dt
        v = A * math.exp(-gamma * t) * math.sin(2 * math.pi * t / T)
        if anomaly and (i // 5) % 2 == 1:
            v = -v                      # phase inversion on alternating windows
        xs.append(round(v, 4))
    return xs


def build(seed=20261001, n_normal=6, n_anom=4, n_transfer=4):
    rng = random.Random(seed)
    observations, probes = [], []
    regimes = [(2.0, 0.10), (3.0, 0.20), (4.0, 0.05), (5.0, 0.30)]

    def series_block(regime, anomaly, count, offset):
        T, g = regime
        out = []
        for i in range(count):
            A = round(1.0 + 0.5 * ((i + offset) % 3), 2)
            xs = gen_series(T, g, A=A, anomaly=anomaly, rng=rng)
            out.append({"series": xs, "T": T, "gamma": g,
                        "anomalous": anomaly})
        return out

    # discovery set: regime A (T=2), mixed normal + anomaly
    observations = series_block(regimes[0], False, n_normal, 0) + \
                   series_block(regimes[0], True, n_anom, 1)
    # transfer probes: regime B (T=3, different gamma/A), same structure
    probes = series_block(regimes[1], False, 2, 0) + \
             series_block(regimes[1], True, 2, 1)
    return observations, probes


CHARTER = ("Below are sampled signals from a physical process. "
           "Some series are NORMAL, some are not. "
           "Report: (a) which series are anomalous, (b) the numeric law "
           "you inferred (period, damping), (c) the rule in one sentence.")
# NOTE the charter does NOT mention the phase-inversion mechanism —
# detecting it is the SURPRISE metric.
