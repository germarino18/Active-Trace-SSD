import React from "react";

/** Checkbox — square check with violet fill when selected. */
export function Checkbox({ checked = false, onChange, disabled = false, label, id }) {
  const inputId = id || React.useId();
  return (
    <label htmlFor={inputId} style={{
      display: "inline-flex", alignItems: "center", gap: 10,
      cursor: disabled ? "not-allowed" : "pointer", opacity: disabled ? 0.5 : 1,
    }}>
      <button
        id={inputId}
        type="button"
        role="checkbox"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => !disabled && onChange && onChange(!checked)}
        style={{
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          width: 18, height: 18, flexShrink: 0, padding: 0,
          borderRadius: "var(--radius-sm)",
          background: checked ? "var(--primary)" : "var(--surface-container-low)",
          border: checked ? "1px solid var(--primary)" : "1px solid var(--outline)",
          cursor: disabled ? "not-allowed" : "pointer",
          transition: "background .15s ease, border-color .15s ease",
        }}
      >
        {checked && <span className="material-symbols-outlined" style={{ fontSize: 16, color: "var(--on-primary)" }}>check</span>}
      </button>
      {label && <span style={{ fontFamily: "var(--font-sans)", fontSize: 14, color: "var(--on-surface)" }}>{label}</span>}
    </label>
  );
}
