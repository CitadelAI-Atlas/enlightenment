# Arc Specification v0: The Program

*Drafted 2026-06-11. Status: pre-research draft. Will be revised after literature
verification (docs/01 open questions), then frozen as v1 before generator work
begins.*

The arc is a **normalized contour**: movement boundaries and events are expressed as
percentages of total session duration. The program is rendered at multiple candidate
medium-length durations, and duration itself is an experimental variable (see the
charter). Peak intensity lands at roughly 55-60 percent of the session, per GIM
contour theory and the Grof phase structure.

## Master structure: five movements, gapless

| # | Movement | Span | Function | Entrainment | Character |
|---|---|---|---|---|---|
| I | Threshold | 0-13% | settle, safety, body | alpha 10 to 8 Hz | warm drone, sparse; breath layer pacing from resting rate toward slow |
| II | Ascent | 13-37% | build, dissolve ordinary attention | theta 8 to 5.5 Hz | percussion enters at 3-4.5 beats per second; density (not tempo) accelerates; 3:4:5 polyrhythm blur in the final third |
| III | Peak | 37-60% | openness, vastness, surrender | theta 5 Hz plus brief gamma shimmer | rhythm falls away; harmonically open; maximum spatial width; brief near-silence window near the midpoint |
| IV | Heart | 60-80% | warmth, meaning | theta to alpha, 5 to 8 Hz | first true melody: the leitmotif blooms; voices re-converge to unison |
| V | Return | 80-100% | grounding, integration | alpha 8 to 10 Hz | theme returns simplified; field collapses to warm center; taper to silence at the close |

## Structural rules

1. **No event is abrupt.** Transitions span roughly 1.5 to 3 percent of total
   duration and happen at the level of musical material, not volume faders.
2. **Intensity is density plus harmonic tension plus register, never loudness
   spikes.** Dynamic range is wide but slow-moving.
3. **Rhythm front-loaded, melody back-loaded** (Grof).
4. **Nested arcs**: each movement contains three to five internal tension and
   release cycles inside the master contour (Bonny).
5. **Entrainment ramps are continuous**, never stepped: beat frequency glides.

## Continuous parameter curves (the spec as data, to be formalized in JSON)

- `entrainment_hz(t)`: beat or pulse frequency over normalized time (the band ramps
  above)
- `breath_rate(t)`: master breathing envelope, easing from a resting rate (about 8
  breaths per minute) to about 5.5 by the 40 percent mark, returning toward 6.5 at
  the close
- `spatial_width(t)`: intimate, then vast at the peak, then warm and centered at the
  return
- `detune_cents(t)`: unison, maximum drift at the peak, audible re-convergence in
  Movement IV
- `rhythmic_density(t)`: zero in Movement I, ramps through II, falls to zero across
  III, low pulse in V
- `harmonic_tension(t)`: Bonny nested cycles superimposed on the master arc

## Singular events (each occurs exactly once)

- Heartbeat: opens the program and returns just before the close
- Rain swell that resolves into the drum pattern: late Movement II
- Distant bell: once, in Movement III
- The near-silence window: Movement III, near the session midpoint
- Unison re-convergence: Movement IV

## Deliverable format

- One gapless master render per candidate duration (48 kHz / 24-bit WAV; FLAC and
  chaptered formats for distribution)
- Per-movement stems for variant swapping
- Layer stems (drone / rhythm / entrainment / breath / events) for the interactive
  player
