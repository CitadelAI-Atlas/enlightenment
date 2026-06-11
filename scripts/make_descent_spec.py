"""Generate the descent-weighted contour variant from the frozen v1 spec.

Remaps every curve breakpoint and event position from the standard movement
boundaries onto descent-weighted boundaries informed by the Copenhagen Music
Program proportions (Messell et al. 2022): shorter ascent, earlier peak, and a
long descent. The curves themselves are unchanged; only their placement in
normalized time moves, so the two contours differ in exactly one way.

Usage: python scripts/make_descent_spec.py
"""

import json
from pathlib import Path

SRC = Path("specs/arc-v1.json")
DST = Path("specs/arc-v1-descent.json")

OLD = [0.0, 0.13, 0.37, 0.6, 0.8, 1.0]
NEW = [0.0, 0.09, 0.27, 0.45, 0.7, 1.0]


def remap(x):
    for i in range(len(OLD) - 1):
        if OLD[i] <= x <= OLD[i + 1]:
            f = (x - OLD[i]) / (OLD[i + 1] - OLD[i])
            return round(NEW[i] + f * (NEW[i + 1] - NEW[i]), 4)
    return x


def main():
    spec = json.loads(SRC.read_text())
    spec["spec_version"] = "1-descent"
    spec["title"] = "Descent-weighted contour variant of arc v1"
    spec["notes"] = (
        "Generated from arc-v1.json by scripts/make_descent_spec.py. Movement "
        "boundaries remapped toward the Copenhagen Music Program proportions "
        "(Messell et al. 2022): shorter ascent, earlier peak, long descent. "
        "Contour shape is an experimental variable; see docs/02."
    )
    for m, (a, b) in zip(spec["movements"], zip(NEW[:-1], NEW[1:])):
        m["span"] = [a, b]
    for name, bps in spec["curves"].items():
        spec["curves"][name] = [[remap(x), y] for x, y in bps]
    for ev in spec["events"].values():
        for key in ("tau", "until_tau"):
            if key in ev:
                ev[key] = remap(ev[key])
    DST.write_text(json.dumps(spec, indent=2) + "\n")
    print("wrote", DST)


if __name__ == "__main__":
    main()
