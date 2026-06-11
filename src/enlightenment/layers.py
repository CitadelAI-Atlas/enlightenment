"""Sound layers. Each layer renders stereo blocks and keeps its own phase state.

All layers read the normalized-time curves from the spec, so the same code
renders the arc at any session duration. Event-style layers (rhythm, melody,
bell, heartbeat) use a carry buffer so event tails cross block boundaries.
"""

import numpy as np

from .noise import Drift

TWO_PI = 2.0 * np.pi


def equal_power_pan(mono, pan):
    """pan in [-1, 1], scalar or per-sample array."""
    angle = (np.asarray(pan) + 1.0) * (np.pi / 4.0)
    return np.stack([mono * np.cos(angle), mono * np.sin(angle)], axis=1)


class BreathEnvelope:
    """Master breathing envelope: swells on the inhale, softens on the exhale.

    Rate follows the breath_bpm curve. When disabled, returns a flat envelope.
    """

    def __init__(self, ctx, depth=0.22):
        self.ctx = ctx
        self.depth = depth if ctx.options["breath"] else 0.0
        self.phase = 0.0

    def block(self, tau, n):
        rate_hz = self.ctx.curves["breath_bpm"].at(tau) / 60.0
        phase = self.phase + np.cumsum(rate_hz) / self.ctx.sr
        self.phase = float(phase[-1])
        # Asymmetric cycle: faster rise (inhale), slower fall (exhale).
        cycle = phase % 1.0
        shape = np.where(
            cycle < 0.42,
            0.5 - 0.5 * np.cos(np.pi * cycle / 0.42),
            0.5 + 0.5 * np.cos(np.pi * (cycle - 0.42) / 0.58),
        )
        return (1.0 - self.depth) + self.depth * shape


class DroneLayer:
    """Harmonic-series drone: chord voices in slow unison drift.

    detune_cents spreads the unison voices (widest at the peak, audibly
    re-converging in the Heart movement). harmonic_tension fades suspended
    tones in and out. Partial phases are exact multiples of each voice phase,
    so glides stay phase-coherent.
    """

    N_PARTIALS = 6

    def __init__(self, ctx):
        self.ctx = ctx
        self.root = ctx.root_hz
        self.voices = []  # (ratio, detune_position, pan_position, gain)
        for ratio, note_gain in zip(ctx.spec["tuning"]["chord_ratios"], (1.0, 0.62, 0.45)):
            for d, pan in ((-1.0, -0.6), (0.0, 0.0), (1.0, 0.6)):
                self.voices.append([ratio, d, pan, note_gain / 3.0])
        self.tension_ratios = ctx.spec["tuning"]["tension_ratios"]
        self.phases = np.zeros(len(self.voices) + len(self.tension_ratios))
        self.partial_amps = 1.0 / np.arange(1, self.N_PARTIALS + 1) ** 1.7
        self.swells = [Drift(ctx.rng, rate=0.08, depth=0.25) for _ in self.voices]
        self.swell_vals = np.zeros(len(self.voices))
        # Nested tension and release cycles inside the master contour (Bonny):
        # several rise-and-fall waves per movement, with a drifting phase so
        # they never align mechanically.
        self.cycle_rate = 14.0
        self.cycle_phase = float(ctx.rng.uniform(0.0, 1.0))
        self.cycle_drift = Drift(ctx.rng, rate=0.04, depth=0.15)

    def render(self, tau, n, breath_env):
        ctx = self.ctx
        cents = ctx.curves["detune_cents"].at(tau)
        width = ctx.curves["spatial_width"].at(tau)
        nested = np.sin(
            TWO_PI * (tau * self.cycle_rate + self.cycle_phase + self.cycle_drift.next())
        )
        gain = ctx.curves["drone_gain"].at(tau) * breath_env * (1.0 + 0.06 * nested)
        tension = np.clip(
            ctx.curves["harmonic_tension"].at(tau) * (1.0 + 0.35 * nested), 0.0, 1.2
        )
        out = np.zeros((n, 2))

        for i, (ratio, d, pan_pos, vgain) in enumerate(self.voices):
            freq = self.root * ratio * 2.0 ** (d * cents / 1200.0)
            phase = self.phases[i] + TWO_PI * np.cumsum(freq) / ctx.sr
            self.phases[i] = float(phase[-1]) % TWO_PI
            mono = np.zeros(n)
            for k in range(1, self.N_PARTIALS + 1):
                mono += self.partial_amps[k - 1] * np.sin(k * phase)
            target = self.swells[i].next()
            swell = 1.0 + np.linspace(self.swell_vals[i], target, n)
            self.swell_vals[i] = target
            mono *= vgain * gain * swell
            out += equal_power_pan(mono, pan_pos * width)

        for j, ratio in enumerate(self.tension_ratios):
            i = len(self.voices) + j
            freq = np.full(n, self.root * 2.0 * ratio)
            phase = self.phases[i] + TWO_PI * np.cumsum(freq) / ctx.sr
            self.phases[i] = float(phase[-1]) % TWO_PI
            mono = np.zeros(n)
            for k in range(1, 4):
                mono += self.partial_amps[k - 1] * np.sin(k * phase)
            mono *= 0.18 * tension * gain
            out += equal_power_pan(mono, (0.3 if j % 2 else -0.3) * width)

        return out * 0.16


class EntrainmentLayer:
    """Binaural or isochronic layer following the entrainment_hz curve.

    Binaural: one carrier per ear, offset by the beat frequency.
    Isochronic: a single carrier amplitude-pulsed at the beat frequency.
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.mode = ctx.options["entrainment"]
        self.carrier = ctx.spec["tuning"]["entrain_carrier_hz"]
        self.phase_l = 0.0
        self.phase_r = 0.0
        self.phase_beat = 0.0

    def render(self, tau, n, breath_env):
        if self.mode == "off":
            return np.zeros((n, 2))
        ctx = self.ctx
        beat = ctx.curves["entrainment_hz"].at(tau)
        gain = 0.045 * ctx.curves["entrain_gain"].at(tau)

        if self.mode == "binaural":
            pl = self.phase_l + TWO_PI * self.carrier * np.arange(1, n + 1) / ctx.sr
            pr = self.phase_r + TWO_PI * np.cumsum(self.carrier + beat) / ctx.sr
            self.phase_l = float(pl[-1]) % TWO_PI
            self.phase_r = float(pr[-1]) % TWO_PI
            return np.stack([np.sin(pl) * gain, np.sin(pr) * gain], axis=1)

        pc = self.phase_l + TWO_PI * self.carrier * np.arange(1, n + 1) / ctx.sr
        pb = self.phase_beat + np.cumsum(beat) / ctx.sr
        self.phase_l = float(pc[-1]) % TWO_PI
        self.phase_beat = float(pb[-1]) % 1.0
        pulse = np.clip(1.7 * (0.5 - 0.5 * np.cos(TWO_PI * pb)) - 0.35, 0.0, 1.0)
        mono = np.sin(pc) * pulse * gain
        return np.stack([mono, mono], axis=1)


class EventScheduler:
    """Shared carry-buffer machinery for layers that place waveforms in time."""

    def __init__(self, ctx, tail_len):
        self.ctx = ctx
        self.carry = np.zeros((tail_len, 2))

    def begin(self, n):
        tail = len(self.carry)
        buf = np.zeros((n + tail, 2))
        buf[:tail] += self.carry
        return buf

    def finish(self, buf, n):
        self.carry = buf[n:].copy()
        return buf[:n]

    def place(self, buf, idx, stereo):
        end = min(idx + len(stereo), len(buf))
        if idx < end:
            buf[idx:end] += stereo[: end - idx]


class RhythmLayer(EventScheduler):
    """Layered percussion at the ceremonial drumming rate.

    Base pulse follows rhythm_rate_hz; amplitude and presence follow
    rhythmic_density. Two side layers at 3:4 and 5:4 of the base rate fade in
    under poly_gain to blur the downbeat in the late ascent. Onset timing and
    amplitude carry correlated drift so the pattern never repeats exactly.
    """

    RATIOS = (1.0, 0.75, 1.25)

    def __init__(self, ctx):
        sr = ctx.sr
        t = np.arange(int(0.3 * sr)) / sr
        freq = 45.0 + 48.0 * np.exp(-t * 16.0)
        body = np.sin(TWO_PI * np.cumsum(freq) / sr) * np.exp(-t * 13.0)
        tap = ctx.rng.standard_normal(len(t)) * np.exp(-t * 140.0) * 0.25
        self.hit = body + tap
        super().__init__(ctx, len(self.hit))
        self.t_next = [0.0, 0.13, 0.21]
        self.time_drift = [Drift(ctx.rng, rate=0.1, depth=0.06) for _ in self.RATIOS]
        self.amp_drift = [Drift(ctx.rng, rate=0.12, depth=0.3) for _ in self.RATIOS]

    def render(self, t0_sec, n, tau_of):
        ctx = self.ctx
        buf = self.begin(n)
        end_sec = t0_sec + n / ctx.sr
        for li, ratio in enumerate(self.RATIOS):
            while self.t_next[li] < end_sec:
                t_hit = self.t_next[li]
                tau = tau_of(t_hit)
                rate = float(ctx.curves["rhythm_rate_hz"].at(tau)) * ratio
                self.t_next[li] = t_hit + (1.0 / max(rate, 0.5)) * (
                    1.0 + self.time_drift[li].next()
                )
                density = float(ctx.curves["rhythmic_density"].at(tau))
                if li > 0:
                    density *= float(ctx.curves["poly_gain"].at(tau))
                if density < 0.01 or t_hit < t0_sec:
                    continue
                if ctx.rng.random() > 0.3 + 0.7 * density:
                    continue
                amp = density * (0.6 + self.amp_drift[li].next() + 0.15 * ctx.rng.random())
                if amp <= 0.0:
                    continue
                width = float(ctx.curves["spatial_width"].at(tau))
                pan = ((li - 1) * 0.45 + 0.15 * self.time_drift[li].value) * width
                idx = int((t_hit - t0_sec) * ctx.sr)
                self.place(buf, idx, equal_power_pan(self.hit * amp * 0.5, pan))
        return self.finish(buf, n)


class MelodyLayer(EventScheduler):
    """The leitmotif, drawn from the harmonic series of the drone root.

    Silent until melody_gain opens in the Heart movement, returning as a
    single simplified voice in the Return. Note level follows the breath
    envelope sampled at onset.
    """

    NOTE_LEN = 12.0
    NOTE_GAP = 8.5

    def __init__(self, ctx):
        sr = ctx.sr
        m = int(self.NOTE_LEN * sr)
        t = np.arange(m) / sr
        attack = np.clip(t / 4.0, 0.0, 1.0) ** 2
        release = np.clip((self.NOTE_LEN - t) / 6.0, 0.0, 1.0) ** 2
        self.env = attack * release
        super().__init__(ctx, m)
        self.partials = ctx.spec["tuning"]["melody_partials"]
        self.note_i = 0
        self.t_next = 0.0
        self.gap_drift = Drift(ctx.rng, rate=0.1, depth=0.12)

    def render(self, t0_sec, n, tau_of):
        ctx = self.ctx
        buf = self.begin(n)
        end_sec = t0_sec + n / ctx.sr
        while self.t_next < end_sec:
            t_note = self.t_next
            self.t_next = t_note + self.NOTE_GAP * (1.0 + self.gap_drift.next())
            tau = tau_of(t_note)
            gain = float(ctx.curves["melody_gain"].at(tau))
            if gain < 0.02 or t_note < t0_sec:
                continue
            partial = self.partials[self.note_i % len(self.partials)]
            self.note_i += 1
            freq = ctx.root_hz * 2.0 * partial / 4.0
            t = np.arange(len(self.env)) / ctx.sr
            mono = (
                np.sin(TWO_PI * freq * t) + 0.3 * np.sin(TWO_PI * 2 * freq * t)
            ) * self.env
            width = float(ctx.curves["spatial_width"].at(tau))
            pan = (0.25 if self.note_i % 2 else -0.25) * width
            idx = int((t_note - t0_sec) * ctx.sr)
            self.place(buf, idx, equal_power_pan(mono * gain * 0.085, pan))
        return self.finish(buf, n)


def _heartbeat_thump(sr):
    t = np.arange(int(0.22 * sr)) / sr
    return np.sin(TWO_PI * 52.0 * t) * np.exp(-t * 22.0)


def _bell(sr, f0):
    ratios = (1.0, 2.76, 5.40, 8.93)
    amps = (1.0, 0.5, 0.28, 0.16)
    decays = (9.0, 6.0, 4.0, 2.5)
    m = int(11.0 * sr)
    t = np.arange(m) / sr
    out = np.zeros(m)
    for r, a, d in zip(ratios, amps, decays):
        out += a * np.sin(TWO_PI * f0 * r * t) * np.exp(-t / d)
    out *= np.clip(t / 0.05, 0.0, 1.0)
    return out / np.max(np.abs(out))


class EventsLayer(EventScheduler):
    """Singular events: the opening and closing heartbeat, one bell, the rain.

    Each occurs exactly once per session. The rain is a filtered noise swell
    late in the Ascent; the bell sounds once in the Peak.
    """

    def __init__(self, ctx):
        self.thump = _heartbeat_thump(ctx.sr)
        self.bell = _bell(ctx.sr, ctx.root_hz * 4.0)
        super().__init__(ctx, len(self.bell))
        # Droplet kernel for the rain: a short bright ping plus a small body,
        # so individual drops read as drops over the noise bed.
        t = np.arange(int(0.006 * ctx.sr)) / ctx.sr
        kern = np.sin(TWO_PI * 3800.0 * t) * np.exp(-t * 900.0)
        kern += 0.4 * np.sin(TWO_PI * 1400.0 * t) * np.exp(-t * 500.0)
        self.drop_kernel = kern * 0.6
        self.rain_drift = Drift(ctx.rng, rate=0.15, depth=0.3)
        ev = ctx.spec["events"]
        self.hb_windows = [
            (ev["heartbeat_open"]["tau"], ev["heartbeat_open"]["until_tau"]),
            (ev["heartbeat_close"]["tau"], ev["heartbeat_close"]["until_tau"]),
        ]
        self.bell_tau = ev["bell"]["tau"]
        self.bell_done = False
        self.rain = ev["rain"]
        self.t_next_beat = 0.0
        self.lp_state = 0.0

    def _heartbeats(self, buf, t0_sec, end_sec, tau_of):
        ctx = self.ctx
        while self.t_next_beat < end_sec:
            t_beat = self.t_next_beat
            self.t_next_beat = t_beat + 1.05
            tau = tau_of(t_beat)
            amp = 0.0
            for a, b in self.hb_windows:
                if a <= tau <= b:
                    pos = (tau - a) / max(b - a, 1e-9)
                    amp = float(np.sin(np.pi * pos)) * 0.5
            if amp <= 0.01 or t_beat < t0_sec:
                continue
            idx = int((t_beat - t0_sec) * ctx.sr)
            self.place(buf, idx, equal_power_pan(self.thump * amp, 0.0))
            idx2 = idx + int(0.32 * ctx.sr)
            self.place(buf, idx2, equal_power_pan(self.thump * amp * 0.6, 0.0))

    def _rain_block(self, tau, n):
        a, b = self.rain["tau"], self.rain["until_tau"]
        pos = (tau - a) / max(b - a, 1e-9)
        env = np.where((pos > 0) & (pos < 1), np.sin(np.pi * np.clip(pos, 0, 1)) ** 2, 0.0)
        if float(np.max(env)) < 1e-4:
            return None
        # Shower intensity wanders rather than swelling symmetrically.
        env = env * (0.75 + 0.25 * abs(self.rain_drift.next()))
        rng = self.ctx.rng
        # Bed: lowpassed noise, the distant wash.
        noise = rng.standard_normal(n)
        bed = np.empty(n)
        k = 0.12
        s = self.lp_state
        for i in range(n):
            s += k * (noise[i] - s)
            bed[i] = s
        self.lp_state = s
        # Droplets: sparse transients, independent per channel, density
        # following the envelope.
        chans = []
        for _ in range(2):
            impulses = np.zeros(n)
            mask = rng.random(n) < env * (320.0 / self.ctx.sr)
            count = int(np.sum(mask))
            if count:
                impulses[mask] = rng.uniform(0.25, 1.0, count)
            chans.append(np.convolve(impulses, self.drop_kernel)[:n])
        out = np.stack([bed * 0.4 + chans[0], bed * 0.4 + chans[1]], axis=1)
        return out * (np.sqrt(env) * 0.2)[:, None]

    def render(self, t0_sec, n, tau_of, tau):
        ctx = self.ctx
        buf = self.begin(n)
        end_sec = t0_sec + n / ctx.sr
        self._heartbeats(buf, t0_sec, end_sec, tau_of)
        bell_t = self.bell_tau * ctx.total_seconds
        if not self.bell_done and t0_sec <= bell_t < end_sec:
            idx = int((bell_t - t0_sec) * ctx.sr)
            self.place(buf, idx, equal_power_pan(self.bell * 0.22, 0.12))
            self.bell_done = True
        out = self.finish(buf, n)
        rain = self._rain_block(tau, n)
        if rain is not None:
            out = out + rain
        return out
