import React from "react";

/** Tag — low-emphasis metadata chip (subject codes, filters, categories). */
export function Tag({ children, icon, onRemove, style }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      height: 24, padding: "0 8px",
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-sm)",
      fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 500,
      color: "var(--on-surface-variant)", whiteSpace: "nowrap",
      ...style,
    }}>
      {icon && <span className="material-symbols-outlined" style={{ fontSize: 14 }}>{icon}</span>}
      {children}
      {onRemove && (
        <span
          className="material-symbols-outlined"
          onClick={onRemove}
          style={{ fontSize: 14, cursor: "pointer", marginLeft: 2 }}
        >close</span>
      )}
    </span>
  );
}
