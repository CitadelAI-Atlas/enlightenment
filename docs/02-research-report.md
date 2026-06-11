# 02 - Research Report: Verification Pass One

*Completed 2026-06-11. This pass verified the working-knowledge claims in
`docs/01-theory-foundations.md` against primary sources before freezing the
arc specification at v1.*

## Method

A multi-agent research harness decomposed the seven open questions from
`docs/01` into six search angles, fetched 25 sources, extracted 115 candidate
claims, and adversarially verified the 25 most load-bearing claims with three
independent verification votes each (a claim dies on two refute votes). Result:
25 confirmed, 0 refuted. Grades below reflect both verification confidence and
the strength of the underlying studies, which are not the same thing: a claim
can be verified as accurately stated while the study itself is small.

## Findings by question

### Q1. Phase structure of the breathwork music protocol (Grof)

**Grade: primary source not located.** No primary-source phase structure,
proportions, or per-phase music characteristics for the Grof breathwork music
protocol were found; the official book listing contains no technical detail.
The canonical description (rhythmic opening, intense middle, heart music,
meditative close) circulates in secondary sources only. **Consequence:** our
"rhythm front-loaded, melody back-loaded" principle is relabeled from
evidence-backed to traditional practice pending consultation of the primary
text (Grof and Grof 2010, SUNY Press).

### Q2. Music's role in supervised clinical sessions

**Grade: moderate.** Kaelen et al. 2018 (Psychopharmacology 235(2):505-519,
DOI 10.1007/s00213-017-4820-5) studied n=19 patients with treatment-resistant
depression in supervised clinical sessions at Imperial College London. The
quality of the music experience significantly predicted symptom reduction at
one week (liking r=0.60, p=.006; resonance r=0.59, p=.008; openness r=0.57,
p=.001) while the intensity of the pharmacological intervention did not
(r=0.004, p=.98). Music had both welcome and unwelcome influences; poorly
fitting music actively harmed sessions. Caveats: small sample, correlational,
single timepoint, unreplicated. **Consequence:** personal resonance and
comfort are first-order design constraints; nothing jarring, demanding, or
culturally narrow.

Related: Strickland, Garcia-Romeu and Johnson 2021 (ACS Pharmacology and
Translational Science, DOI 10.1021/acsptsci.0c00187, n=10) compared
overtone-based music against Western classical in supervised sessions:
peak-experience scores trended higher for overtone-based material (d_z=0.57)
but did not reach significance. **Grade: weak but directionally encouraging**
for this project's drone and overtone aesthetic.

### Q3. Auditory beat stimulation, pooled effects

**Grade: moderate for behavioral and subjective outcomes.** Two distinct
meta-analyses, not to be conflated: Garcia-Argibay, Santed and Reales 2019
(Psychological Research 83(2):357-372) pooled 22 studies (35 effect sizes)
and found a medium overall effect (Hedges' g=0.45) across memory, attention,
anxiety, and pain perception, with **longer exposure duration a significant
moderator** (favorable for extended programs). Basu and Banerjee 2023
(Psychological Research 87(4):951-963) pooled 15 studies: g=0.40 on memory
and attention combined, with the systematic-review component reporting
conflicting results in several bands. See Q6 for the mechanism caveat.

### Q4. GIM program structure and intensity contour

**Grade: moderate for the contour shape, qualitative only.** Verified: Bonny's
GIM listening programs are sequences of five to eight classical selections
lasting 25-50 minutes inside 90-120 minute sessions. A published affect
contour exists (Meadows 2010, Voices 10(3), reproducing Bonny 2002): a
build-peak-return shape, graphical rather than numeric. The underlying
six-phase session model traces to Bonny and Pahnke 1972 (Journal of Music
Therapy 9(2):64-87), from clinical research at the Maryland Psychiatric
Research Center.

The unexpected finding: Grocke's phenomenological study of pivotal moments in
GIM (7 clients) found that peak therapeutic moments coincided with music that
was **slow, stable, formally structured, repetitive, and predictable**
(diatonic, consonant, repeated rhythmic motifs), not with climactic novelty.
Small-sample qualitative evidence, but it directly shaped v1 (see below).

### Q5. Quiet intervals at peak intensity

**Grade: no controlled evidence at peak; adjacent support for silence after
music.** A 2025 systematic review (Stolterfoth and Pfeifer, The Arts in
Psychotherapy, DOI 10.1016/j.aip.2025.102286) found only 5 of 89 candidate
studies tested silence in receptive music interventions at all, and every one
placed the silence after the music, never at peak intensity within a program.
Adjacent finding: Bernardi, Porta and Sleight 2006 (Heart) measured greater
cardiovascular relaxation during a two-minute silent pause between tracks than
during the music itself. **Consequences:** the quiet interval stays in the
program as an explicitly exploratory variable (our trial would be among the
first controlled tests of it), and the listening protocol now recommends
several minutes of silence after the program ends, which is the placement the
evidence actually supports.

### Q6. Mechanism honesty: does beat stimulation entrain brain oscillations?

**Grade: unsettled, and the spec language now reflects that.** Ingendoh, Posny
and Heine 2023 (PLOS One) reviewed 14 EEG studies of binaural beats: 5
supporting entrainment, 8 contradicting, 1 mixed. The one head-to-head study
(dos Anjos et al. 2024, Neuroscience, n=28, 4-minute stimulation) found
isochronic tones produced significantly greater EEG power changes than
binaural beats, and that white noise matched binaural beats on gamma-band
measures, which argues against a frequency-specific mechanism for binaural
beats specifically. Single small study, unreplicated. **Consequences:** the
pooled behavioral effects in Q3 stand, but we no longer describe the layer as
producing entrainment; it is auditory beat stimulation with a contested
mechanism. The isochronic variant is fully justified as a comparison arm, and
hypothesis H2's expectations are tempered accordingly.

### Q7. Session duration

**Grade: the one-to-three-hour band is bracketed but unpopulated.** Verified
anchors: GIM listening programs run 25-50 minutes (sessions 90-120 minutes)
below our band; the Copenhagen Music Program (Messell et al. 2022, Frontiers
in Psychology 13:873455) sits above it, a quantified three-phase template of
Ascent 51 minutes, Peak 80 minutes, Descent 209 minutes, roughly 5.7 hours,
built for extended supervised clinical sessions. No study directly compares
receptive-listening durations within our band. **Consequences:** our duration
trials address a genuine gap, and the Copenhagen proportions (15 percent
ascent, 24 percent peak, 61 percent descent) motivated a descent-weighted
alternate contour as a new experimental variable.

### Flagged side topics

- **Breath pacing through musical phrasing: evidence not located** in this
  pass (the relevant primary literature, such as Bernardi et al. 2006 on music
  and respiration, was not fetched and verified here). Hypothesis H1 is
  therefore more novel than we assumed: even its premise is currently
  unverified, which raises both its risk and its scientific value.
- **Ceremonial drumming rates overlapping the theta band: evidence not
  located.** The claim circulates widely but no primary source survived this
  pass. The drumming rate in our program is relabeled as traditional precedent
  and aesthetic choice until the original EEG work is verified.

"Not located" means exactly that: these were not refuted, and dedicated
follow-up on the named primary sources is queued for pass two.

## Design consequences adopted in spec v1

1. **Peak stability principle** (from Grocke): harmonic tension now peaks in
   the late Ascent and declines through the Peak, which favors stable,
   consonant, predictable material at maximum depth. No new musical material
   is introduced during the Peak.
2. **Contour becomes an experimental variable**: v1 ships two frozen contours,
   the standard arc and a descent-weighted alternate informed by the
   Copenhagen proportions.
3. **Quiet interval relabeled exploratory**, kept as a variable; post-program
   silence added to the listening protocol.
4. **Mechanism language corrected** throughout: auditory beat stimulation, not
   entrainment.
5. **Drumming rate relabeled** traditional precedent.
6. **H1 flagged as novel**: its premise (listeners pace breath to musical
   phrasing) is itself untested as far as this pass could verify.

## Open questions for pass two

1. The Grof primary text and official training materials (Q1 core).
2. Primary studies on respiratory entrainment to music (Bernardi et al. 2006
   and successors).
3. The original drumming EEG work (Maxfield) and any successors.
4. Whether any study anywhere tests silence at peak intensity within an
   ongoing program; if none, our trial design should be written up carefully
   since it would be a first.

## Primary sources verified in this pass

- Kaelen et al. 2018, Psychopharmacology 235(2):505-519
- Strickland, Garcia-Romeu, Johnson 2021, ACS Pharmacology and Translational Science
- Garcia-Argibay, Santed, Reales 2019, Psychological Research 83(2):357-372
- Basu, Banerjee 2023, Psychological Research 87(4):951-963
- Messell et al. 2022, Frontiers in Psychology 13:873455
- Meadows 2010, Voices 10(3); Bonny and Pahnke 1972, Journal of Music Therapy 9(2):64-87
- Grocke 1999/2010 (University of Melbourne; Voices)
- Stolterfoth, Pfeifer 2025, The Arts in Psychotherapy
- Ingendoh, Posny, Heine 2023, PLOS One
- dos Anjos et al. 2024, Neuroscience
- Bernardi, Porta, Sleight 2006, Heart
