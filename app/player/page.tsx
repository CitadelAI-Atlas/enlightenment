"use client";

import { useEffect, useRef, useState } from "react";
import arcStandard from "@/specs/arc-v1.json";
import arcDescent from "@/specs/arc-v1-descent.json";
import { JourneyEngine, type ArcSpec, type PlayerOptions } from "./synth";

const SPECS: Record<string, ArcSpec> = {
  standard: arcStandard as ArcSpec,
  descent: arcDescent as ArcSpec,
};

const DURATIONS = [20, 45, 90, 150];

function fmt(sec: number) {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  return h
    ? `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`
    : `${m}:${String(s).padStart(2, "0")}`;
}

export default function PlayerPage() {
  const [contour, setContour] = useState<"standard" | "descent">("standard");
  const [duration, setDuration] = useState(45);
  const [beat, setBeat] = useState<PlayerOptions["beat"]>("binaural");
  const [breath, setBreath] = useState(true);
  const [quiet, setQuiet] = useState(true);
  const [tuning, setTuning] = useState<440 | 432>(440);
  const [running, setRunning] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [finished, setFinished] = useState(false);
  const [calm, setCalm] = useState(4);
  const [absorption, setAbsorption] = useState(4);
  const [notes, setNotes] = useState("");
  const engine = useRef<JourneyEngine | null>(null);

  const spec = SPECS[contour];
  const T = duration * 60;
  const tau = T ? elapsed / T : 0;
  const movement = spec.movements.find((m) => tau >= m.span[0] && tau <= m.span[1]);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => setElapsed(engine.current?.elapsed ?? 0), 1000);
    return () => clearInterval(id);
  }, [running]);

  const start = async () => {
    setFinished(false);
    const e = new JourneyEngine({ spec, durationMin: duration, beat, breath, quiet, tuning });
    e.onend = () => {
      setRunning(false);
      setFinished(true);
    };
    engine.current = e;
    await e.start();
    setRunning(true);
  };

  const stop = () => {
    engine.current?.stop();
    setRunning(false);
    if (elapsed > 60) setFinished(true);
  };

  const variant = { contour, duration_min: duration, beat, breath, quiet, tuning };

  const reportBody = [
    "## Session report",
    "",
    "Configuration (auto-attached):",
    "```json",
    JSON.stringify({ ...variant, spec_version: spec.spec_version, completed_min: Math.round(elapsed / 60) }, null, 2),
    "```",
    "",
    `Calm or settled afterward (1 low to 7 high): ${calm}`,
    `Absorption during the session (1 low to 7 high): ${absorption}`,
    "",
    "Notes (what stood out, by movement if possible):",
    notes || "(none)",
  ].join("\n");

  const issueUrl =
    "https://github.com/CitadelAI-Atlas/enlightenment/issues/new?title=" +
    encodeURIComponent(`Session report: ${contour} contour, ${beat}, ${duration} min`) +
    "&labels=session-report&body=" +
    encodeURIComponent(reportBody);

  return (
    <div className="player">
      <h1>Player</h1>
      <p>
        This player synthesizes the program live in your browser from the frozen
        v1 specification, at a candidate session length you choose. Every control
        below is an experimental variable. Use headphones; on Apple headphones,
        turn off Spatialize Audio and head tracking. The downloadable renders
        remain the canonical trial material.
      </p>

      <div className="controls">
        <label>
          Contour
          <select value={contour} disabled={running} onChange={(e) => setContour(e.target.value as "standard" | "descent")}>
            <option value="standard">standard</option>
            <option value="descent">descent-weighted</option>
          </select>
        </label>
        <label>
          Length (min)
          <select value={duration} disabled={running} onChange={(e) => setDuration(Number(e.target.value))}>
            {DURATIONS.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <label>
          Beat stimulation
          <select
            value={beat}
            onChange={(e) => {
              const v = e.target.value as PlayerOptions["beat"];
              setBeat(v);
              engine.current?.setBeat(v);
            }}
          >
            <option value="binaural">binaural</option>
            <option value="isochronic">isochronic</option>
            <option value="off">off</option>
          </select>
        </label>
        <label>
          Breath layer
          <select
            value={breath ? "on" : "off"}
            onChange={(e) => {
              const v = e.target.value === "on";
              setBreath(v);
              engine.current?.setBreath(v);
            }}
          >
            <option value="on">on</option>
            <option value="off">off</option>
          </select>
        </label>
        <label>
          Quiet interval
          <select
            value={quiet ? "on" : "off"}
            onChange={(e) => {
              const v = e.target.value === "on";
              setQuiet(v);
              engine.current?.setQuiet(v);
            }}
          >
            <option value="on">on</option>
            <option value="off">off</option>
          </select>
        </label>
        <label>
          Tuning
          <select value={tuning} disabled={running} onChange={(e) => setTuning(Number(e.target.value) as 440 | 432)}>
            <option value={440}>440 Hz</option>
            <option value={432}>432 Hz</option>
          </select>
        </label>
      </div>

      <div className="transport">
        {!running ? (
          <button onClick={start}>Begin session</button>
        ) : (
          <button onClick={stop}>End session</button>
        )}
        <span className="time">
          {fmt(elapsed)} / {fmt(T)}
          {movement ? ` · ${movement.name}` : ""}
        </span>
      </div>

      <div className="timeline">
        {spec.movements.map((m) => (
          <div
            key={m.name}
            className={"seg" + (movement?.name === m.name && running ? " active" : "")}
            style={{ width: `${(m.span[1] - m.span[0]) * 100}%` }}
            title={m.name}
          >
            {m.name}
          </div>
        ))}
      </div>
      {running && <div className="cursor" style={{ marginLeft: `${tau * 100}%` }} />}

      {finished && (
        <div className="report">
          <h2>Session report</h2>
          <p>
            Reports are public and become part of the open dataset. Submitting
            opens a prefilled GitHub issue you can review before posting.
          </p>
          <label>
            Calm or settled afterward: {calm}
            <input type="range" min={1} max={7} value={calm} onChange={(e) => setCalm(Number(e.target.value))} />
          </label>
          <label>
            Absorption during the session: {absorption}
            <input type="range" min={1} max={7} value={absorption} onChange={(e) => setAbsorption(Number(e.target.value))} />
          </label>
          <label>
            Notes
            <textarea
              rows={5}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="What stood out, by movement if possible. Anything jarring. Where attention went."
            />
          </label>
          <div className="report-actions">
            <a className="button" href={issueUrl} target="_blank" rel="noreferrer">
              Submit as public GitHub issue
            </a>
            <button onClick={() => navigator.clipboard.writeText(reportBody)}>Copy report text</button>
          </div>
        </div>
      )}
    </div>
  );
}
