"""Block renderer: mixes all layers and streams a 24-bit WAV to disk.

Renders in one-second blocks so sessions of any length use constant memory.
All randomness comes from a single seeded generator, so any render is exactly
reproducible from (spec, duration, options, seed).
"""

import json
import wave

import numpy as np

from .curves import load_curves
from .layers import (
    BreathEnvelope,
    DroneLayer,
    EntrainmentLayer,
    EventsLayer,
    MelodyLayer,
    RhythmLayer,
)


class Context:
    def __init__(self, spec, sr, duration_min, options, seed):
        self.spec = spec
        self.sr = sr
        self.total_seconds = duration_min * 60.0
        self.total_samples = int(self.total_seconds * sr)
        self.options = options
        self.rng = np.random.default_rng(seed)
        self.curves = load_curves(spec)
        ratio = 432.0 / 440.0 if options["tuning"] == 432 else 1.0
        self.root_hz = spec["tuning"]["root_hz_at_440"] * ratio


def _to_24bit_bytes(stereo):
    ints = np.clip(stereo, -1.0, 1.0)
    ints = (ints * 8388607.0).astype("<i4")
    raw = ints.reshape(-1).view(np.uint8).reshape(-1, 4)[:, :3]
    return raw.tobytes()


def _quiet_dip(ctx, tau):
    ev = ctx.spec["events"]["quiet_interval"]
    if not ctx.options["quiet"]:
        return np.ones_like(tau)
    g = np.exp(-0.5 * ((tau - ev["tau"]) / ev["width_tau"]) ** 2)
    return 1.0 - (1.0 - ev["floor"]) * g


def render(spec_path, duration_min, out_path, options, seed=1, sr=48000, progress=None):
    with open(spec_path) as f:
        spec = json.load(f)
    ctx = Context(spec, sr, duration_min, options, seed)
    breath = BreathEnvelope(ctx)
    drone = DroneLayer(ctx)
    entrain = EntrainmentLayer(ctx)
    rhythm = RhythmLayer(ctx)
    melody = MelodyLayer(ctx)
    events = EventsLayer(ctx)

    def tau_of(t_sec):
        return min(max(t_sec / ctx.total_seconds, 0.0), 1.0)

    movements = spec["movements"]
    stats = {m["name"]: {"peak": 0.0, "sumsq": 0.0, "n": 0} for m in movements}

    wav = wave.open(str(out_path), "wb")
    wav.setnchannels(2)
    wav.setsampwidth(3)
    wav.setframerate(sr)

    block = sr
    i = 0
    while i < ctx.total_samples:
        n = min(block, ctx.total_samples - i)
        t = (i + np.arange(n)) / sr
        tau = t / ctx.total_seconds
        t0_sec = i / sr

        env = breath.block(tau, n)
        mix = drone.render(tau, n, env)
        mix += entrain.render(tau, n, env)
        mix += rhythm.render(t0_sec, n, tau_of)
        mix += melody.render(t0_sec, n, tau_of)
        mix += events.render(t0_sec, n, tau_of, tau)

        gain = ctx.curves["master_gain"].at(tau) * _quiet_dip(ctx, tau)
        mix *= gain[:, None]
        mix = np.tanh(1.2 * mix) / np.tanh(1.2)

        mid = float(tau[n // 2])
        for m in movements:
            if m["span"][0] <= mid <= m["span"][1]:
                s = stats[m["name"]]
                s["peak"] = max(s["peak"], float(np.max(np.abs(mix))))
                s["sumsq"] += float(np.sum(mix**2))
                s["n"] += mix.size
                break

        wav.writeframes(_to_24bit_bytes(mix))
        i += n
        if progress and (i // block) % 60 == 0:
            progress(i / ctx.total_samples)

    wav.close()
    return {
        name: {
            "peak": round(s["peak"], 3),
            "rms_db": round(10 * np.log10(max(s["sumsq"] / max(s["n"], 1), 1e-12)), 1),
        }
        for name, s in stats.items()
    }
