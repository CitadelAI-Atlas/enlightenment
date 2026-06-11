# 05 - Generator Design (v1)

*Written 2026-06-11*

The generator is a Python synthesis pipeline (`src/enlightenment/`, numpy only)
that renders the arc specification at any requested session duration.

## Design principles

1. **The spec is data, the generator is code.** The arc lives in
   `specs/arc-*.json` as normalized-time curves (x from 0 to 1) and singular
   events. The renderer evaluates those curves at whatever duration is
   requested, so revising or freezing the spec never requires code changes,
   and duration trials reuse one implementation.
2. **Exact reproducibility.** All randomness flows from one seeded generator.
   A render is fully determined by (spec, duration, options, seed): we
   verified that identical inputs produce byte-identical files. Any trial can
   therefore be reproduced or audited from its logged parameters.
3. **Constant memory.** Audio streams to disk in one-second blocks (24-bit,
   48 kHz stereo WAV), so session length never strains memory.
4. **Every experimental variable is a flag.** Entrainment (binaural,
   isochronic, off), breath layer (on, off), quiet interval (on, off),
   reference tuning (440, 432), seed, and duration are all command-line
   options. Variant renders for blind comparison differ in exactly one flag.

## Layers

- **Drone**: harmonic-series voices over a root chord, with unison detune
  following `detune_cents` (widest at the peak, audibly re-converging in the
  Heart movement) and suspended tones faded by `harmonic_tension`. Partial
  phases are exact multiples of voice phase, keeping glides coherent.
- **Breath envelope**: a master swell at `breath_bpm`, asymmetric like a real
  breath cycle (faster rise, slower fall), applied to the drone.
- **Entrainment**: binaural (one carrier per ear offset by `entrainment_hz`)
  or isochronic (single carrier, amplitude-pulsed). Verified by spectral
  measurement of the rendered file: the interaural difference matches the
  spec curve.
- **Rhythm**: synthesized drum at the ceremonial drumming rate, with 3:4 and
  5:4 side layers fading in under `poly_gain` to blur the downbeat in the
  late Ascent. Onset timing and amplitude carry correlated drift (a bounded
  random walk), so the pattern never repeats exactly.
- **Melody**: the leitmotif, drawn from the harmonic series of the drone
  root, silent until `melody_gain` opens in the Heart movement.
- **Events**: the opening and closing heartbeat, one rain swell late in the
  Ascent, one bell in the Peak, and the optional quiet interval at the
  session midpoint. Each occurs exactly once.

## Usage

```
python -m enlightenment --spec specs/arc-v0.json --duration-min <N> \
  --entrainment binaural|isochronic|off --breath on|off --quiet on|off \
  --tuning 440|432 --seed <int> --out renders/<name>.wav
```

Duration is always explicit. It is an experimental variable, never a default.

## Distribution formats

The 24-bit WAV is the archival reference (reproducible from spec, options, and
seed, so it is never committed). For distribution, `scripts/encode.sh`
produces:

- **MP3, 320 kbps CBR, forced left/right stereo.** Joint stereo is disabled
  on purpose: the entrainment layer depends on each channel keeping its own
  carrier. Verified by decoding the MP3 and re-measuring the interaural
  difference at the session midpoint: 5.00 Hz against a spec value of 5.0,
  unchanged from the WAV.
- **AAC, 256 kbps (m4a)** as a smaller alternative.

A full-length session encodes to roughly one seventh of the WAV size as MP3.

## Listening protocol notes

- Headphones are required for the binaural variant; the beat frequency exists
  only when each ear receives its own carrier.
- On Apple headphones, disable Spatialize Audio and head tracking for trials.
  Spatial processing remixes the channels through HRTF filters and would
  degrade the interaural separation. Noise cancellation is fine.

## Changes in generator v0.2 (2026-06-11, after the first shakedown listen)

- **Rain rebuilt.** The first listen flagged that the rain read as wind: it
  was a lowpassed noise swell with no droplet detail. It is now a noise bed
  plus sparse droplet transients (bright 6 ms pings, independent per channel,
  density following the envelope), with shower intensity that wanders rather
  than swelling symmetrically. Verified by band analysis: droplet-band energy
  is present in the rain window where there was effectively none.
- **Nested tension cycles implemented** (Bonny): a slow rise-and-fall wave,
  several cycles per movement with drifting phase, now modulates harmonic
  tension and drone level inside the master contour. This addresses the
  "very stable" note from the shakedown listen without touching the frozen
  v1 contour, which this modulation sits inside.
- **Cue sheets and chapters.** `scripts/cuesheet.py` generates a table of
  contents for any render (movement and event times at the chosen duration)
  plus chapter metadata that `scripts/encode.sh` embeds in the m4a.

## Known limitations (v0.2)

- The gamma shimmer overlay at the peak is deferred.
- The rain recedes but does not yet resolve rhythmically into the drum
  pattern.
- The leitmotif is not yet planted as overtone coloration in the Threshold
  (creative commitment 4); it first appears in the Heart.
- Render verification is spectral and statistical; listening trials are the
  real test.
