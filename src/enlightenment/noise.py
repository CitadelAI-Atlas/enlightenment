"""Correlated random variation sources.

Natural music exhibits 1/f (pink) fluctuation rather than white randomness.
These helpers provide slowly drifting control values so that timing, amplitude,
and timbre evolve like weather instead of jittering or looping.
"""

import numpy as np


class Drift:
    """One-pole filtered noise: a bounded random walk with 1/f-like character.

    Sampled at control rate (once per request), suitable for modulating onset
    timing, hit amplitude, and swell depth.
    """

    def __init__(self, rng, rate=0.05, depth=1.0):
        self.rng = rng
        self.rate = rate
        self.depth = depth
        self.value = 0.0

    def next(self):
        self.value += self.rate * (self.rng.standard_normal() - 0.3 * self.value)
        return float(np.clip(self.value * self.depth, -1.0, 1.0))


def pink_block(rng, n, octaves=8):
    """Voss-McCartney pink noise block, normalized to roughly unit variance."""
    total = np.zeros(n)
    for o in range(octaves):
        step = 2 ** o
        m = n // step + 2
        vals = rng.standard_normal(m)
        total += np.repeat(vals, step)[:n]
    return total / np.sqrt(octaves)
