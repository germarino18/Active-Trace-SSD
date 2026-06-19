import React from "react";

/**
 * Badge — small status pill. Tones: primary, success, danger, neutral, warning.
 * Style: "soft" (tinted bg + colored text, default) or "solid". Optional dot.
 */
export function Badge({ children, tone = "neutral", variant = "soft", dot = false, icon, style }) {
  const tones = {
    primary: { fg: "var(--primary)", solidBg: "var(--primary)", solidFg: "var(--on-primary)" },
    success: { fg: "var(--tertiary)", solidBg: "var(--tertiary)", solidFg: "var(--on-tertiary)" },
    danger: { fg: "var(--error)", solidBg: "var(--error)", solidFg: "var(--on-error)" },
    warning: { fg: "#fbbf24", solidBg: "#fbbf24", solidFg: "#1a1200" },
    neutral: { fg: "var(--on-surface-variant)", solidBg: "var(--secondary-container)", solidFg: "var(--on-surface)" },
  };
  const t = tones[tone] || tones.neutral;

  const soft = {
    background: `color-mix(in srgb, ${t.fg} 14%, transparent)`,
    color: t.fg,
    border: `1px solid color-mix(in srgb, ${t.fg} 28%, transparent)`,
  };
  const solid = { background: t.solidBg, color: t.solidFg, border: "1px solid transparent" };

  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      height: 22, padding: "0 10px",
      borderRadius: "var(--radius-full)",
      fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 600,
      letterSpacing: "0.02em", lineHeight: 1, whiteSpace: "nowrap",
      ...(variant === "solid" ? solid : soft),
      ...style,
    }}>
      {dot && <span style={{ width: 6, height: 6, borderRadius: "var(--radius-full)", background: "currentColor" }} />}
      {icon && <span className="material-symbols-outlined" style={{ fontSize: 14 }}>{icon}</span>}
      {children}
    </span>
  );
}
