import React from "react";

/** ProgressBar — thin track. Tones: primary, success. Optional segmented mode. */
export function ProgressBar({ value = 0, tone = "primary", height = 8, label, showValue = false, segments, style }) {
  const color = tone === "success" ? "var(--tertiary)" : "var(--primary)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, width: "100%", ...style }}>
      {(label || showValue) && (
        <div style={{ display: "flex", justifyContent: "space-between", fontFamily: "var(--font-sans)", fontSize: 11, fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase", color: "var(--on-surface-variant)" }}>
          {label && <span>{label}</span>}
          {showValue && <span>{Math.round(value)}%</span>}
        </div>
      )}
      <div style={{ display: "flex", width: "100%", height, borderRadius: "var(--radius-full)", background: "var(--surface-container-highest)", overflow: "hidden" }}>
        {segments
          ? segments.map((seg, i) => (
              <div key={i} style={{ width: `${seg.value}%`, height: "100%", background: seg.color || color }} />
            ))
          : <div style={{ width: `${Math.min(100, Math.max(0, value))}%`, height: "100%", background: color, borderRadius: "var(--radius-full)", transition: "width 1s ease" }} />}
      </div>
    </div>
  );
}
