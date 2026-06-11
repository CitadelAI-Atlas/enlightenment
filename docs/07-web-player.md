# 07 - The Web Player

*Written 2026-06-11. Live at /player on the project site.*

The player is the experiment's public instrument: it synthesizes the program
live in the browser from the same frozen specification the offline generator
uses, and turns listeners into participants.

## How it works

- **Same spec, second realization.** The player imports `specs/arc-v1.json`
  and `specs/arc-v1-descent.json` directly and evaluates the same normalized
  curves with the Web Audio API: the harmonic-series drone with detune and
  nested tension cycles, the breath envelope, binaural or isochronic beat
  stimulation, the percussion layers, the leitmotif, and the singular events.
  No audio files are downloaded; the program is generated on the device.
- **Every experimental variable is a control**: contour (standard or
  descent-weighted), candidate session length, beat stimulation mode, breath
  layer, quiet interval, and reference tuning. Beat mode, breath, and the
  quiet interval can be toggled live during a session.
- **Session reports are public.** After a session (or an early stop past the
  first minute), the report form collects two ratings (calm, absorption) and
  free notes, attaches the exact configuration automatically, and submits as
  a prefilled public GitHub issue labeled `session-report`. The dataset grows
  in the open, and every report carries the variant that produced it.

## Honest limitations

- The live synthesis is a faithful approximation, not the canonical render:
  browser scheduling is not sample-deterministic, the rain is simplified, and
  there is no seed. **Offline renders remain the trial material**; the player
  is for exploration, variant comparison, and crowd participation.
- Submitting a report requires a GitHub account (the price of a public,
  attributable, zero-infrastructure dataset; an anonymous channel may come
  later).
- Self-selected, unblinded listeners: player reports are hypothesis-generating
  context, never confirmatory data. The charter's grading rules apply.

## Protocol reminders shown in the player

Headphones required for the binaural variant; on Apple headphones, disable
Spatialize Audio and head tracking. Plan a few minutes of silence after the
session ends.
