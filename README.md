# Enlightenment

An open experiment in long-form meditation music, and an attempt to understand one
small corner of how the mind responds to structured sound. We design, generate, and
empirically test extended music programs for deep meditative listening, then publish
everything: theory, strategy, models, inspiration, trial and error, including what
does not work.

**Live site:** https://enlightenment-sigma.vercel.app ·
**Repository:** https://github.com/CitadelAI-Atlas/enlightenment

## What this is

We are building a parameterized music generator that renders a five-movement
meditation program grounded in three documented traditions:

1. **Bonny's Guided Imagery and Music (GIM)**: affect-contour theory of receptive
   music-therapy programs
2. **Grof's holotropic breathwork music protocol**: the closest precedent for
   extended, arc-structured listening
3. **Receptive-music research from clinical settings** (Johns Hopkins, Imperial
   College London) and the brainwave-entrainment literature

Every theoretical claim is a parameter in the generator. Every parameter is a
testable variable. Listeners are participants: the published player will let you
toggle experimental layers and submit session reports.

## Session length

Programs are medium length by design: substantially longer than a typical guided
meditation, long enough for a complete arc of settling, deepening, opening, and
return. We treat exact duration as an experimental variable to be tested, not an
assumption to be defended.

## Scientific stance

We hold this work to a deliberately cautious standard:

- **Claims are graded.** Every design element is labeled evidence-backed,
  speculative, or aesthetic. We never present an aesthetic choice as a mechanism.
- **Hypotheses precede trials.** They are committed publicly and timestamped before
  any listening session, and results are published whether they support us or not.
- **We know the limits of our methods.** Early trials are small in number, unblinded
  where noted, and self-reported. We treat them as exploration that generates
  hypotheses, not proof. Stronger designs (blinding, crowd-sourced replication)
  come later.
- **The mind is not a lock and sound is not a key.** Music can support and deepen
  meditative states; the literature does not support claims that any frequency or
  rhythm reliably produces a specific state in everyone. We design for support, and
  we measure rather than assume.
- **No medical claims.** This is not therapy or medical advice. The program is built
  for meditation and breathwork practice; session safety is the listener's
  responsibility.

## Repository layout

- `docs/`: theory, design decisions, and methodology (numbered, in order written)
- `specs/`: formal specifications of the program (the arc as data)
- `journal/`: dated lab notebook: what we tried, what happened, what we changed
- `src/`: the generator (Python, numpy; see `docs/05-generator-design.md`)
- `renders/`: audio output (reproducible from spec, options, and seed; not
  committed)

## Principles

- **Open everything.** Hypotheses are stated before trials. Negative results are
  published.
- **Mechanism honesty.** We distinguish evidence-backed elements (breath pacing, arc
  structure) from speculative ones (binaural beats: modest evidence) and aesthetic
  ones (432 Hz tuning: no controlled evidence, included as a testable variable, not
  a claim).
- **Alive, not mechanical.** Generated does not mean looped. Natural variation,
  singular events, and emergent melody are core design commitments. See
  `docs/03-creative-direction.md`.

## Status

**Phase 2: Trials.** Verification pass one is complete (25 claims adversarially
verified, 0 refuted; see `docs/02-research-report.md`) and the arc is frozen at
v1 in two contour variants. Generator v1 renders either contour
deterministically at any duration. Next: first listening trials and research
pass two.
