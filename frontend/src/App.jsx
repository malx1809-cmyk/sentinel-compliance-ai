import { useState, useRef, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

const STAGE_MESSAGES = [
  "Evader is constructing a disguise...",
  "Detector is analyzing signals...",
  "Adjudicator is reviewing the round...",
];

function OutcomeBadge({ outcome }) {
  const styles = {
    caught: "bg-detector/15 text-detector border-detector/40",
    evaded: "bg-evader/15 text-evader border-evader/40",
    error: "bg-muted/15 text-muted border-muted/40",
  };
  const labels = { caught: "CAUGHT", evaded: "EVADED", error: "ERROR" };
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-medium border ${styles[outcome]}`}>
      {labels[outcome]}
    </span>
  );
}

function PulseChart({ rounds, totalRounds }) {
  const width = 640;
  const height = 180;
  const midY = height / 2;
  const leftPad = 30;
  const rightPad = 20;
  const usableWidth = width - leftPad - rightPad;

  let caughtCount = 0;
  const detectorPoints = [];
  const evaderPoints = [];

  const validRounds = rounds.filter((r) => r.outcome !== "error");

  validRounds.forEach((r, i) => {
    if (r.outcome === "caught") caughtCount += 1;
    const catchRate = (caughtCount / (i + 1)) * 100;
    const evadeRate = 100 - catchRate;
    const x = leftPad + (usableWidth * i) / Math.max(totalRounds - 1, 1);
    const detectorY = midY + (catchRate / 100) * (midY - 20);
    const evaderY = midY - (evadeRate / 100) * (midY - 20);
    detectorPoints.push(`${x},${detectorY}`);
    evaderPoints.push(`${x},${evaderY}`);
  });

  const catchRateNow = validRounds.length
    ? Math.round((caughtCount / validRounds.length) * 100)
    : 0;
  const evadeRateNow = 100 - catchRateNow;

  return (
    <div className="bg-surface border border-border rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="font-mono text-xs text-evader tracking-wide">EVADER SUCCESS</p>
          <p className="font-display text-3xl font-semibold text-evader">{evadeRateNow}%</p>
        </div>
        <div className="text-center">
          <p className="font-mono text-xs text-muted tracking-widest">ADVERSARIAL PULSE</p>
        </div>
        <div className="text-right">
          <p className="font-mono text-xs text-detector tracking-wide">DETECTOR CATCH RATE</p>
          <p className="font-display text-3xl font-semibold text-detector">{catchRateNow}%</p>
        </div>
      </div>

      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-40">
        <line x1={leftPad} y1={midY} x2={width - rightPad} y2={midY}
          stroke="#25324D" strokeWidth="1" strokeDasharray="4 4" />

        {evaderPoints.length > 1 && (
          <polyline points={evaderPoints.join(" ")} fill="none" stroke="#FF6B5B"
            strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        )}
        {detectorPoints.length > 1 && (
          <polyline points={detectorPoints.join(" ")} fill="none" stroke="#2FD8BE"
            strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
        )}

        {evaderPoints.map((p, i) => {
          const [x, y] = p.split(",");
          const isLast = i === evaderPoints.length - 1;
          return (
            <circle key={`e-${i}`} cx={x} cy={y} r={isLast ? 5 : 3}
              fill="#FF6B5B" className={isLast ? "pulse-dot" : ""} />
          );
        })}
        {detectorPoints.map((p, i) => {
          const [x, y] = p.split(",");
          const isLast = i === detectorPoints.length - 1;
          return (
            <circle key={`d-${i}`} cx={x} cy={y} r={isLast ? 5 : 3}
              fill="#2FD8BE" className={isLast ? "pulse-dot" : ""} />
          );
        })}
      </svg>
    </div>
  );
}

function RoundCard({ round, expanded, onToggle }) {
  const borderColor =
    round.outcome === "caught" ? "border-l-detector" :
    round.outcome === "evaded" ? "border-l-evader" : "border-l-muted";

  return (
    <div
      onClick={onToggle}
      className={`round-flash bg-surface border border-border ${borderColor} border-l-4 rounded-xl p-4 cursor-pointer hover:bg-surface-2 transition-colors`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs text-muted">ROUND {round.round}</span>
          <span className="text-sm text-text">{round.risk_category}</span>
        </div>
        <OutcomeBadge outcome={round.outcome} />
      </div>

      {expanded && round.outcome !== "error" && (
        <div className="mt-4 pt-4 border-t border-border grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="font-mono text-xs text-evader mb-1">EVADER STRATEGY</p>
            <p className="text-muted mb-2">{round.evader.disguise_strategy}</p>
            <p className="font-mono text-xs text-text">
              ₹{round.evader.transaction.amount.toLocaleString("en-IN")} · {round.evader.transaction.description}
            </p>
          </div>
          <div>
            <p className="font-mono text-xs text-detector mb-1">DETECTOR RATIONALE</p>
            <p className="text-muted mb-2">{round.detector.rationale}</p>
            <p className="font-mono text-xs text-text">
              Risk score: {round.detector.composite_risk_score}/100
            </p>
          </div>
          <div className="md:col-span-2 bg-surface-2 rounded-lg p-3">
            <p className="font-mono text-xs text-amber mb-1">ADJUDICATOR VERDICT</p>
            <p className="text-muted">{round.verdict.reasoning}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [rounds, setRounds] = useState([]);
  const [status, setStatus] = useState("idle");
  const [expandedRound, setExpandedRound] = useState(null);
  const [stageMsg, setStageMsg] = useState(STAGE_MESSAGES[0]);
  const eventSourceRef = useRef(null);
  const totalRounds = 5;

  useEffect(() => {
    if (status !== "running") return;
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % STAGE_MESSAGES.length;
      setStageMsg(STAGE_MESSAGES[i]);
    }, 2200);
    return () => clearInterval(interval);
  }, [status]);

  const startSimulation = () => {
    setRounds([]);
    setExpandedRound(null);
    setStatus("running");

    const es = new EventSource(`${API_BASE}/simulate/stream?rounds=${totalRounds}`);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setRounds((prev) => [...prev, data]);
      if (data.round >= totalRounds) {
        es.close();
        setStatus("done");
      }
    };

    es.onerror = () => {
      es.close();
      setStatus((prev) => (prev === "running" ? "done" : prev));
    };
  };

  return (
    <div className="min-h-screen bg-ink">
      <nav className="border-b border-border px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-detector pulse-dot" />
          <span className="font-display font-semibold text-lg tracking-tight">SENTINEL</span>
        </div>
        <div className="flex items-center gap-6 font-mono text-xs text-muted">
          <span className="text-text">Live Arena</span>
          <span className="opacity-40">Cases</span>
          <span className="opacity-40">Graph</span>
          <span className="opacity-40">Reports</span>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-display text-2xl font-semibold">Adversarial Compliance Simulation</h1>
            <p className="text-muted text-sm mt-1">
              {status === "idle" && "Ready to start a live simulation round."}
              {status === "running" && (
                <span className="font-mono text-amber">{stageMsg}</span>
              )}
              {status === "done" && "Simulation complete."}
            </p>
          </div>
          <button
            onClick={startSimulation}
            disabled={status === "running"}
            className="bg-detector text-ink font-medium px-5 py-2.5 rounded-lg hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
          >
            {status === "running" ? "Running..." : "Start Simulation"}
          </button>
        </div>

        <PulseChart rounds={rounds} totalRounds={totalRounds} />

        <div className="mt-8 space-y-3">
          {rounds.length === 0 && status === "idle" && (
            <div className="text-center py-16 text-muted border border-dashed border-border rounded-2xl">
              <p className="font-mono text-sm">No rounds yet. Click "Start Simulation" to begin.</p>
            </div>
          )}
          {[...rounds].reverse().map((r) => (
            <RoundCard
              key={r.round}
              round={r}
              expanded={expandedRound === r.round}
              onToggle={() => setExpandedRound(expandedRound === r.round ? null : r.round)}
            />
          ))}
        </div>
      </main>
    </div>
  );
}