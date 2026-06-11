"use client";

/* Real-time Web Audio realization of the arc specification.
 *
 * Reads the same normalized-contour spec JSON as the offline generator and
 * synthesizes the program in the browser at a chosen duration. This is a
 * faithful approximation for interactive exploration; the offline renders
 * remain the canonical trial material (deterministic, seedable, verified).
 */

type Breakpoints = number[][];

export interface ArcSpec {
  spec_version: string;
  movements: { name: string; span: number[] }[];
  curves: Record<string, Breakpoints>;
  events: Record<string, { tau: number; until_tau?: number; width_tau?: number; floor?: number }>;
  tuning: {
    root_hz_at_440: number;
    chord_ratios: number[];
    tension_ratios: number[];
    melody_partials: number[];
    entrain_carrier_hz: number;
  };
}

export interface PlayerOptions {
  spec: ArcSpec;
  durationMin: number;
  beat: "binaural" | "isochronic" | "off";
  breath: boolean;
  quiet: boolean;
  tuning: 440 | 432;
}

class Curve {
  xs: number[];
  ys: number[];
  constructor(bps: Breakpoints) {
    this.xs = bps.map((b) => b[0]);
    this.ys = bps.map((b) => b[1]);
  }
  at(x: number): number {
    const { xs, ys } = this;
    if (x <= xs[0]) return ys[0];
    if (x >= xs[xs.length - 1]) return ys[ys.length - 1];
    let i = 1;
    while (xs[i] < x) i++;
    const f = (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
    return ys[i - 1] + f * (ys[i] - ys[i - 1]);
  }
}

const LOOKAHEAD = 8; // seconds scheduled ahead
const TICK = 2; // scheduler interval, seconds

export class JourneyEngine {
  private ctx: AudioContext;
  private opts: PlayerOptions;
  private curves: Record<string, Curve> = {};
  private root: number;
  private T: number;
  private t0 = 0;
  private timer: ReturnType<typeof setInterval> | null = null;
  private scheduledUntil = 0;

  private master!: GainNode;
  private breathGain!: GainNode;
  private droneGain!: GainNode;
  private tensionGain!: GainNode;
  private beatGain!: GainNode;
  private voices: { osc: OscillatorNode; pan: StereoPannerNode; dpos: number }[] = [];
  private beatNodes: AudioNode[] = [];
  private noiseBuf!: AudioBuffer;

  // event scheduling state
  private rhythmNext = [0, 0.13, 0.21];
  private heartNext = 0;
  private melodyNext = 0;
  private melodyIdx = 0;
  private bellDone = false;
  private breathPhaseT = 0; // absolute time of current breath cycle start
  private nestedPhase = Math.random();

  onend: (() => void) | null = null;

  constructor(opts: PlayerOptions) {
    const AC = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.ctx = new AC();
    this.opts = opts;
    this.T = opts.durationMin * 60;
    for (const [name, bps] of Object.entries(opts.spec.curves)) {
      this.curves[name] = new Curve(bps);
    }
    this.root = opts.spec.tuning.root_hz_at_440 * (opts.tuning === 432 ? 432 / 440 : 1);
  }

  get elapsed(): number {
    return this.t0 ? Math.min(this.ctx.currentTime - this.t0, this.T) : 0;
  }
  get tau(): number {
    return this.elapsed / this.T;
  }
  get running(): boolean {
    return this.timer !== null;
  }

  setBreath(on: boolean) {
    this.opts.breath = on;
  }
  setQuiet(on: boolean) {
    this.opts.quiet = on;
  }
  setBeat(mode: PlayerOptions["beat"]) {
    if (mode === this.opts.beat) return;
    this.opts.beat = mode;
    this.teardownBeat();
    if (mode !== "off") this.buildBeat();
  }

  async start() {
    await this.ctx.resume();
    this.t0 = this.ctx.currentTime + 0.1;
    this.noiseBuf = this.makeNoise();
    this.buildGraph();
    this.scheduledUntil = this.t0;
    this.breathPhaseT = this.t0;
    this.timer = setInterval(() => this.tick(), TICK * 1000);
    this.tick();
  }

  stop() {
    if (this.timer) clearInterval(this.timer);
    this.timer = null;
    try {
      this.ctx.close();
    } catch {
      /* already closed */
    }
  }

  private makeNoise(): AudioBuffer {
    const n = this.ctx.sampleRate * 2;
    const buf = this.ctx.createBuffer(1, n, this.ctx.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
    return buf;
  }

  private periodicWave(partials: number, rolloff: number): PeriodicWave {
    const real = new Float32Array(partials + 1);
    const imag = new Float32Array(partials + 1);
    for (let k = 1; k <= partials; k++) imag[k] = 1 / Math.pow(k, rolloff);
    return this.ctx.createPeriodicWave(real, imag);
  }

  private buildGraph() {
    const { ctx } = this;
    this.master = ctx.createGain();
    this.master.gain.value = 0;
    this.master.connect(ctx.destination);

    this.breathGain = ctx.createGain();
    this.breathGain.connect(this.master);

    this.droneGain = ctx.createGain();
    this.droneGain.gain.value = 0;
    this.droneGain.connect(this.breathGain);

    const wave = this.periodicWave(6, 1.7);
    const noteGains = [1.0, 0.62, 0.45];
    this.opts.spec.tuning.chord_ratios.forEach((ratio, ni) => {
      [-1, 0, 1].forEach((dpos) => {
        const osc = ctx.createOscillator();
        osc.setPeriodicWave(wave);
        osc.frequency.value = this.root * ratio;
        const g = ctx.createGain();
        g.gain.value = (noteGains[ni] / 3) * 0.16;
        const pan = ctx.createStereoPanner();
        osc.connect(g).connect(pan).connect(this.droneGain);
        osc.start();
        this.voices.push({ osc, pan, dpos });
      });
    });

    this.tensionGain = ctx.createGain();
    this.tensionGain.gain.value = 0;
    this.tensionGain.connect(this.breathGain);
    this.opts.spec.tuning.tension_ratios.forEach((ratio, i) => {
      const osc = ctx.createOscillator();
      osc.setPeriodicWave(this.periodicWave(3, 1.7));
      osc.frequency.value = this.root * 2 * ratio;
      const pan = ctx.createStereoPanner();
      pan.pan.value = i % 2 ? 0.3 : -0.3;
      osc.connect(pan).connect(this.tensionGain);
      osc.start();
    });

    this.beatGain = ctx.createGain();
    this.beatGain.gain.value = 0;
    this.beatGain.connect(this.master);
    if (this.opts.beat !== "off") this.buildBeat();
  }

  private buildBeat() {
    const { ctx } = this;
    const carrier = this.opts.spec.tuning.entrain_carrier_hz;
    if (this.opts.beat === "binaural") {
      const mk = (panVal: number) => {
        const osc = ctx.createOscillator();
        osc.frequency.value = carrier;
        const pan = ctx.createStereoPanner();
        pan.pan.value = panVal;
        osc.connect(pan).connect(this.beatGain);
        osc.start();
        this.beatNodes.push(osc, pan);
        return osc;
      };
      mk(-1);
      const right = mk(1);
      right.frequency.value = carrier + this.curves.entrainment_hz.at(this.tau);
      (right as OscillatorNode & { __isRight?: boolean }).__isRight = true;
    } else {
      const osc = ctx.createOscillator();
      osc.frequency.value = carrier;
      const pulsed = ctx.createGain();
      pulsed.gain.value = 0;
      const lfo = ctx.createOscillator();
      lfo.frequency.value = this.curves.entrainment_hz.at(this.tau);
      const shaper = ctx.createWaveShaper();
      const curve = new Float32Array(256);
      for (let i = 0; i < 256; i++) {
        const x = (i / 255) * 2 - 1;
        curve[i] = Math.max(0, Math.min(1, 1.7 * (0.5 + 0.5 * x) - 0.35));
      }
      shaper.curve = curve;
      lfo.connect(shaper).connect(pulsed.gain);
      osc.connect(pulsed).connect(this.beatGain);
      osc.start();
      lfo.start();
      this.beatNodes.push(osc, lfo, pulsed, shaper);
    }
  }

  private teardownBeat() {
    for (const n of this.beatNodes) {
      try {
        (n as OscillatorNode).stop?.();
      } catch {
        /* not an oscillator */
      }
      n.disconnect();
    }
    this.beatNodes = [];
  }

  private quietDip(tau: number): number {
    const q = this.opts.spec.events.quiet_interval;
    if (!this.opts.quiet || !q.width_tau) return 1;
    const g = Math.exp(-0.5 * Math.pow((tau - q.tau) / q.width_tau, 2));
    return 1 - (1 - (q.floor ?? 0.04)) * g;
  }

  /* Schedule continuous parameters and discrete events ahead of playback. */
  private tick() {
    const now = this.ctx.currentTime;
    const end = Math.min(now + LOOKAHEAD, this.t0 + this.T);
    if (now >= this.t0 + this.T) {
      this.stop();
      this.onend?.();
      return;
    }
    let t = Math.max(this.scheduledUntil, now);

    for (; t < end; t += 1) {
      const tau = Math.min((t - this.t0) / this.T, 1);
      const nested = Math.sin(2 * Math.PI * (tau * 14 + this.nestedPhase));
      this.master.gain.linearRampToValueAtTime(
        this.curves.master_gain.at(tau) * this.quietDip(tau) * 0.9,
        t,
      );
      this.droneGain.gain.linearRampToValueAtTime(
        this.curves.drone_gain.at(tau) * (1 + 0.06 * nested),
        t,
      );
      this.tensionGain.gain.linearRampToValueAtTime(
        Math.max(0, this.curves.harmonic_tension.at(tau) * (1 + 0.35 * nested)) * 0.03,
        t,
      );
      this.beatGain.gain.linearRampToValueAtTime(
        this.opts.beat === "off" ? 0 : 0.045 * this.curves.entrain_gain.at(tau),
        t,
      );
      const cents = this.curves.detune_cents.at(tau);
      const width = this.curves.spatial_width.at(tau);
      for (const v of this.voices) {
        v.osc.detune.linearRampToValueAtTime(v.dpos * cents, t);
        v.pan.pan.linearRampToValueAtTime(v.dpos * 0.6 * width, t);
      }
      for (const n of this.beatNodes) {
        const osc = n as OscillatorNode & { __isRight?: boolean };
        if (osc.__isRight) {
          osc.frequency.linearRampToValueAtTime(
            this.opts.spec.tuning.entrain_carrier_hz + this.curves.entrainment_hz.at(tau),
            t,
          );
        } else if (osc.frequency && osc.frequency.value < 20) {
          osc.frequency.linearRampToValueAtTime(this.curves.entrainment_hz.at(tau), t);
        }
      }
    }

    this.scheduleBreath(end);
    this.scheduleRhythm(end);
    this.scheduleHeartbeats(end);
    this.scheduleMelody(end);
    this.scheduleBellAndRain(end);
    this.scheduledUntil = end;
  }

  private scheduleBreath(end: number) {
    const depth = this.opts.breath ? 0.22 : 0;
    while (this.breathPhaseT < end) {
      const tau = (this.breathPhaseT - this.t0) / this.T;
      const period = 60 / this.curves.breath_bpm.at(Math.max(0, tau));
      const peak = this.breathPhaseT + 0.42 * period;
      const g = this.breathGain.gain;
      g.linearRampToValueAtTime(1 - depth, Math.max(this.breathPhaseT, this.ctx.currentTime));
      g.linearRampToValueAtTime(1, peak);
      g.linearRampToValueAtTime(1 - depth, this.breathPhaseT + period);
      this.breathPhaseT += period;
    }
  }

  private hit(t: number, amp: number, pan: number) {
    const { ctx } = this;
    const osc = ctx.createOscillator();
    osc.frequency.setValueAtTime(90, t);
    osc.frequency.exponentialRampToValueAtTime(45, t + 0.25);
    const g = ctx.createGain();
    g.gain.setValueAtTime(amp * 0.5, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + 0.28);
    const p = ctx.createStereoPanner();
    p.pan.value = pan;
    osc.connect(g).connect(p).connect(this.master);
    osc.start(t);
    osc.stop(t + 0.3);
  }

  private scheduleRhythm(end: number) {
    const ratios = [1.0, 0.75, 1.25];
    for (let li = 0; li < 3; li++) {
      while (this.t0 + this.rhythmNext[li] * 1 < end) {
        const tAbs = this.t0 + this.rhythmNext[li];
        const tau = this.rhythmNext[li] / this.T;
        const rate = this.curves.rhythm_rate_hz.at(tau) * ratios[li];
        this.rhythmNext[li] += (1 / Math.max(rate, 0.5)) * (1 + (Math.random() - 0.5) * 0.08);
        let density = this.curves.rhythmic_density.at(tau);
        if (li > 0) density *= this.curves.poly_gain.at(tau);
        if (density < 0.01 || tAbs < this.ctx.currentTime) continue;
        if (Math.random() > 0.3 + 0.7 * density) continue;
        const width = this.curves.spatial_width.at(tau);
        this.hit(tAbs, density * (0.6 + 0.3 * Math.random()), (li - 1) * 0.45 * width);
      }
    }
  }

  private scheduleHeartbeats(end: number) {
    const ev = this.opts.spec.events;
    const windows = [
      [ev.heartbeat_open.tau, ev.heartbeat_open.until_tau ?? 0],
      [ev.heartbeat_close.tau, ev.heartbeat_close.until_tau ?? 1],
    ];
    while (this.t0 + this.heartNext < end) {
      const tAbs = this.t0 + this.heartNext;
      const tau = this.heartNext / this.T;
      this.heartNext += 1.05;
      let amp = 0;
      for (const [a, b] of windows) {
        if (tau >= a && tau <= b) amp = Math.sin(Math.PI * ((tau - a) / Math.max(b - a, 1e-9))) * 0.5;
      }
      if (amp < 0.02 || tAbs < this.ctx.currentTime) continue;
      for (const [dt, scale] of [
        [0, 1],
        [0.32, 0.6],
      ]) {
        const osc = this.ctx.createOscillator();
        osc.frequency.value = 52;
        const g = this.ctx.createGain();
        g.gain.setValueAtTime(amp * scale, tAbs + dt);
        g.gain.exponentialRampToValueAtTime(0.001, tAbs + dt + 0.2);
        osc.connect(g).connect(this.master);
        osc.start(tAbs + dt);
        osc.stop(tAbs + dt + 0.25);
      }
    }
  }

  private scheduleMelody(end: number) {
    const partials = this.opts.spec.tuning.melody_partials;
    while (this.t0 + this.melodyNext < end) {
      const tAbs = this.t0 + this.melodyNext;
      const tau = this.melodyNext / this.T;
      this.melodyNext += 8.5 * (1 + (Math.random() - 0.5) * 0.2);
      const gain = this.curves.melody_gain.at(tau);
      if (gain < 0.02 || tAbs < this.ctx.currentTime) continue;
      const p = partials[this.melodyIdx % partials.length];
      this.melodyIdx++;
      const osc = this.ctx.createOscillator();
      osc.setPeriodicWave(this.periodicWave(2, 1.2));
      osc.frequency.value = (this.root * 2 * p) / 4;
      const g = this.ctx.createGain();
      g.gain.setValueAtTime(0, tAbs);
      g.gain.linearRampToValueAtTime(gain * 0.085, tAbs + 4);
      g.gain.setValueAtTime(gain * 0.085, tAbs + 6);
      g.gain.linearRampToValueAtTime(0, tAbs + 12);
      const pan = this.ctx.createStereoPanner();
      pan.pan.value = (this.melodyIdx % 2 ? 0.25 : -0.25) * this.curves.spatial_width.at(tau);
      osc.connect(g).connect(pan).connect(this.breathGain);
      osc.start(tAbs);
      osc.stop(tAbs + 12.5);
    }
  }

  private scheduleBellAndRain(end: number) {
    const ev = this.opts.spec.events;
    const bellT = this.t0 + ev.bell.tau * this.T;
    if (!this.bellDone && bellT >= this.ctx.currentTime && bellT < end) {
      this.bellDone = true;
      const ratios = [1, 2.76, 5.4, 8.93];
      const amps = [1, 0.5, 0.28, 0.16];
      const decays = [9, 6, 4, 2.5];
      ratios.forEach((r, i) => {
        const osc = this.ctx.createOscillator();
        osc.frequency.value = this.root * 4 * r;
        const g = this.ctx.createGain();
        g.gain.setValueAtTime(0, bellT);
        g.gain.linearRampToValueAtTime(amps[i] * 0.06, bellT + 0.05);
        g.gain.exponentialRampToValueAtTime(0.0005, bellT + decays[i]);
        osc.connect(g).connect(this.master);
        osc.start(bellT);
        osc.stop(bellT + decays[i] + 0.5);
      });
    }

    // Rain: droplet pings over the window; the noise bed is approximated by
    // ping density alone in the live player.
    const a = ev.rain.tau;
    const b = ev.rain.until_tau ?? a;
    for (let t = Math.max(this.scheduledUntil, this.ctx.currentTime); t < end; t += 0.25) {
      const tau = (t - this.t0) / this.T;
      const pos = (tau - a) / Math.max(b - a, 1e-9);
      if (pos <= 0 || pos >= 1) continue;
      const env = Math.pow(Math.sin(Math.PI * pos), 2);
      const count = Math.floor(env * 2 + Math.random());
      for (let i = 0; i < count; i++) {
        const tp = t + Math.random() * 0.25;
        const osc = this.ctx.createOscillator();
        osc.frequency.value = 2800 + Math.random() * 2200;
        const g = this.ctx.createGain();
        const amp = env * 0.02 * (0.3 + Math.random());
        g.gain.setValueAtTime(amp, tp);
        g.gain.exponentialRampToValueAtTime(0.0005, tp + 0.04);
        const pan = this.ctx.createStereoPanner();
        pan.pan.value = Math.random() * 1.4 - 0.7;
        osc.connect(g).connect(pan).connect(this.master);
        osc.start(tp);
        osc.stop(tp + 0.06);
      }
    }
  }
}
