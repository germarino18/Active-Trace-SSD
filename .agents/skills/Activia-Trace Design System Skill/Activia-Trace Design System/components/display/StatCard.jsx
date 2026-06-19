import React from "react";

/**
 * StatCard — KPI tile. Big number, label, optional trend + progress bar.
 * tone="primary" renders the filled violet highlight variant.
 */
export function StatCard({ label, value, unit, trend, trendDir = "up", icon, progress, tone = "default", style }) {
  const filled = tone === "primary";
  const trendColor = trendDir === "down" ? "var(--error)" : "var(--tertiary)";

  return (
    <div style={{
      display: "flex", flexDirection: "column", justifyContent: "space-between", gap: 16,
      minHeight: 130, padding: 24, borderRadius: "var(--radius-lg)",
      background: filled ? "var(--primary-container)" : "var(--surface-container)",
      color: filled ? "var(--on-primary-container)" : "var(--on-surface)",
      border: filled ? "1px solid color-mix(in srgb, var(--primary) 25%, transparent)" : "1px solid var(--outline-variant)",
      ...style,
    }}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <span style={{
          fontFamily: "var(--font-sans)", fontSize: 11, fontWeight: 600,
          letterSpacing: "0.05em", textTransform: "uppercase",
          color: filled ? "color-mix(in srgb, var(--on-primary-container) 80%, transparent)" : "var(--on-surface-variant)",
        }}>{label}</span>
        {icon && <span className="material-symbols-outlined" style={{ fontSize: 20, color: filled ? "var(--on-primary-container)" : "var(--primary)" }}>{icon}</span>}
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
        <span style={{ fontFamily: "var(--font-sans)", fontSize: 36, fontWeight: 800, letterSpacing: "-0.02em", lineHeight: 1 }}>{value}</span>
        {unit && <span style={{ fontSize: 16, fontWeight: 600, opacity: 0.5 }}>{unit}</span>}
      </div>

      {trend && (
        <div style={{ display: "flex", alignItems: "center", gap: 4, fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 500, color: filled ? "inherit" : trendColor }}>
          <span className="material-symbols-outlined" style={{ fontSize: 16 }}>{trendDir === "down" ? "trending_down" : "trending_up"}</span>
          {trend}
        </div>
      )}

      {typeof progress === "number" && (
        <div style={{ width: "100%", height: 6, borderRadius: "var(--radius-full)", background: filled ? "color-mix(in srgb, var(--on-primary-container) 20%, transparent)" : "var(--surface-container-highest)", overflow: "hidden" }}>
          <div style={{ width: `${Math.min(100, Math.max(0, progress))}%`, height: "100%", background: filled ? "var(--on-primary-container)" : "var(--tertiary)", borderRadius: "var(--radius-full)" }} />
        </div>
      )}
    </div>
  );
}
