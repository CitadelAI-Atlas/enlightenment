"""Command-line entry point.

Example:
    python -m enlightenment --spec specs/arc-v0.json --duration-min 20 \
        --entrainment binaural --breath on --quiet on --tuning 440 \
        --seed 1 --out renders/test.wav

Session duration is always explicit: it is an experimental variable, never a
default.
"""

import argparse
import sys
import time
from pathlib import Path

from .render import render


def main(argv=None):
    p = argparse.ArgumentParser(prog="enlightenment")
    p.add_argument("--spec", required=True)
    p.add_argument("--duration-min", type=float, required=True)
    p.add_argument("--out", default=None)
    p.add_argument("--entrainment", choices=["binaural", "isochronic", "off"], default="binaural")
    p.add_argument("--breath", choices=["on", "off"], default="on")
    p.add_argument("--quiet", choices=["on", "off"], default="on")
    p.add_argument("--tuning", type=int, choices=[440, 432], default=440)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--sr", type=int, default=48000)
    args = p.parse_args(argv)

    options = {
        "entrainment": args.entrainment,
        "breath": args.breath == "on",
        "quiet": args.quiet == "on",
        "tuning": args.tuning,
    }
    out = args.out
    if out is None:
        spec_name = Path(args.spec).stem
        variant = "{}-{}-breath_{}-quiet_{}-{}hz-seed{}".format(
            spec_name, args.entrainment, args.breath, args.quiet, args.tuning, args.seed
        )
        out = "renders/{}-{}min.wav".format(variant, int(args.duration_min))
    Path(out).parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    stats = render(
        args.spec,
        args.duration_min,
        out,
        options,
        seed=args.seed,
        sr=args.sr,
        progress=lambda f: print("  {:.0%}".format(f), flush=True),
    )
    elapsed = time.time() - start

    print("Rendered {} in {:.1f}s".format(out, elapsed))
    print("Per-movement levels (peak / RMS dBFS):")
    for name, s in stats.items():
        print("  {:<10} peak {:.3f}   rms {} dB".format(name, s["peak"], s["rms_db"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
