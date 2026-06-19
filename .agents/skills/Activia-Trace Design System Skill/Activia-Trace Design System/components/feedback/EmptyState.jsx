import React from "react";

/**
 * EmptyState — centered placeholder for empty tables, error screens (403/404),
 * and "no results" views. Icon in a tinted circle, title, message, optional action.
 */
export function EmptyState({ icon = "inbox", title, message, action, code, style }) {
  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
      textAlign: "center", padding: 48, gap: 8, ...style,
    }}>
      {code ? (
        <div style={{ fontFamily: "var(--font-sans)", fontSize: 72, fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1, color: "var(--primary)" }}>{code}</div>
      ) : (
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "center",
          width: 64, height: 64, borderRadius: "var(--radius-full)",
          background: "color-mix(in srgb, var(--primary) 12%, transparent)",
          color: "var(--primary)", marginBottom: 8,
        }}>
          <span className="material-symbols-outlined" style={{ fontSize: 32 }}>{icon}</span>
        </div>
      )}
      <h3 style={{ margin: 0, fontFamily: "var(--font-sans)", fontSize: 20, fontWeight: 700, color: "var(--on-surface)" }}>{title}</h3>
      {message && <p style={{ margin: 0, maxWidth: 420, fontFamily: "var(--font-sans)", fontSize: 14, lineHeight: 1.5, color: "var(--on-surface-variant)" }}>{message}</p>}
      {action && <div style={{ marginTop: 16 }}>{action}</div>}
    </div>
  );
}
