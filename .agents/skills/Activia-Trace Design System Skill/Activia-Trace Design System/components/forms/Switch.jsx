import React from "react";

/** Switch — Material-style toggle. On = violet track, knob slides right. */
export function Switch({ checked = false, onChange, disabled = false, label, id }) {
  const inputId = id || React.useId();
  return (
    <label htmlFor={inputId} style={{
      display: "inline-flex", alignItems: "center", gap: 10,
      cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.5 : 1,
    }}>
      <button
        id={inputId}
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange && onChange(!checked)}
        style={{
          position: "relative", width: 40, height: 20, flexShrink: 0,
          borderRadius: "var(--radius-full)",
          background: checked ? "var(--primary)" : "var(--surface-container-highest)",
          border: checked ? "1px solid transparent" : "1px solid var(--outline-variant)",
          cursor: disabled ? "not-allowed" : "pointer",
          transition: "background .2s ease",
          padding: 0,
        }}
      >
        <span style={{
          position: "absolute", top: 2, left: 2,
          width: 16, height: 16, borderRadius: "var(--radius-full)",
          background: checked ? "var(--on-primary)" : "var(--on-surface-variant)",
          transform: checked ? "translateX(20px)" : "translateX(0)",
          transition: "transform .2s ease",
        }} />
      </button>
      {label && <span style={{ fontFamily: "var(--font-sans)", fontSize: 14, color: "var(--on-surface)" }}>{label}</span>}
    </label>
  );
}
