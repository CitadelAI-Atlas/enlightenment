"""Generate a cue sheet and chapter metadata for a render.

Reads a spec and a session duration and writes a human-readable table of
contents (markdown) plus an ffmetadata chapter file that scripts/encode.sh
embeds into the m4a, so players show movement chapters.

Usage: python scripts/cuesheet.py --spec specs/arc-v1.json --duration-min 150 \
    --out renders/arc-v1-150min
"""

import argparse
import json
from pathlib import Path

MOVEMENT_NOTES = {
    "Threshold": "Warm drone, sparse. Breath pacing eases from resting rate toward slow.",
    "Ascent": "Percussion enters and densifies. Harmonic tension crests late in this movement; polyrhythm blur in the final third.",
    "Peak": "Rhythm falls away. Stable, consonant, harmonically open; maximum spatial width.",
    "Heart": "First true melody: the leitmotif blooms. Detuned voices re-converge to unison.",
    "Return": "Theme returns simplified. Field narrows to a warm center; taper to silence.",
}


def fmt(sec):
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return "{}:{:02d}:{:02d}".format(h, m, s) if h else "{}:{:02d}".format(m, s)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spec", required=True)
    p.add_argument("--duration-min", type=float, required=True)
    p.add_argument("--out", required=True, help="output path prefix (no extension)")
    args = p.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    T = args.duration_min * 60.0
    ev = spec["events"]

    rows = []
    for m in spec["movements"]:
        a, b = m["span"]
        rows.append((a * T, "Movement: " + m["name"], MOVEMENT_NOTES.get(m["name"], "")))
    rows.append((ev["heartbeat_open"]["tau"] * T, "Opening heartbeat", "Fades out by {}".format(fmt(ev["heartbeat_open"]["until_tau"] * T))))
    rows.append((ev["rain"]["tau"] * T, "Rain swell", "Builds and recedes until {}".format(fmt(ev["rain"]["until_tau"] * T))))
    rows.append((ev["bell"]["tau"] * T, "Bell", "Single occurrence"))
    q = ev["quiet_interval"]
    rows.append((q["tau"] * T, "Near-silence interval", "Exploratory variable; about {} wide".format(fmt(q["width_tau"] * T * 4))))
    rows.append((ev["heartbeat_close"]["tau"] * T, "Closing heartbeat", "Carries to the end"))
    rows.sort(key=lambda r: r[0])

    md = ["# Cue sheet: {} at {} minutes".format(Path(args.spec).stem, int(args.duration_min)), ""]
    md.append("| Time | Section or event | Notes |")
    md.append("|---|---|---|")
    for t, name, note in rows:
        md.append("| {} | {} | {} |".format(fmt(t), name, note))
    Path(args.out + "-cuesheet.md").write_text("\n".join(md) + "\n")

    meta = [";FFMETADATA1"]
    spans = [m["span"] for m in spec["movements"]]
    for m, (a, b) in zip(spec["movements"], spans):
        meta += [
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            "START={}".format(int(a * T * 1000)),
            "END={}".format(int(b * T * 1000)),
            "title={}".format(m["name"]),
        ]
    Path(args.out + ".ffmeta").write_text("\n".join(meta) + "\n")
    print("wrote {0}-cuesheet.md and {0}.ffmeta".format(args.out))


if __name__ == "__main__":
    main()
