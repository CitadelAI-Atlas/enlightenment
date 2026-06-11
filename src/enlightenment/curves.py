"""Piecewise-linear curves over normalized session time (tau in [0, 1])."""

import numpy as np


class Curve:
    def __init__(self, breakpoints):
        pts = sorted((float(x), float(y)) for x, y in breakpoints)
        self.xs = np.array([p[0] for p in pts])
        self.ys = np.array([p[1] for p in pts])

    def at(self, tau):
        return np.interp(tau, self.xs, self.ys)


def load_curves(spec):
    return {name: Curve(bps) for name, bps in spec["curves"].items()}
