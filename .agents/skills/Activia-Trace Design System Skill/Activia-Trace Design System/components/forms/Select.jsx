import React from "react";

/** Select — native dropdown styled to match Input. Pass options=[{value,label}] or children. */
export function Select({ label, value, onChange, options, children, placeholder, disabled = false, error, id, style, ...rest }) {
  const [focused, setFocused] = React.useState(false);
  const inputId = id || React.useId();
  const borderColor = error ? "var(--error)" : focused ? "var(--primary)" : "var(--outline-variant)";
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, width: "100%" }}>
      {label && (
        <label htmlFor={inputId} style={{
          fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 600,
          letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--on-surface-variant)",
        }}>{label}</label>
      )}
      <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
        <select
          id={inputId}
          value={value}
          onChange={onChange}
          disabled={disabled}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          style={{
            width: "100%",
            height: 40,
            padding: "0 40px 0 14px",
            background: "var(--surface-container-low)",
            color: value ? "var(--on-surface)" : "var(--outline)",
            border: `1px solid ${borderColor}`,
            borderRadius: "var(--radius-md)",
            fontFamily: "var(--font-sans)",
            fontSize: 14,
            appearance: "none",
            WebkitAppearance: "none",
            outline: "none",
            cursor: disabled ? "not-allowed" : "pointer",
            opacity: disabled ? 0.5 : 1,
            boxShadow: focused && !error ? "0 0 0 2px color-mix(in srgb, var(--primary) 30%, transparent)" : "none",
            transition: "border-color .15s ease, box-shadow .15s ease",
            ...style,
          }}
          {...rest}
        >
          {placeholder && <option value="" disabled>{placeholder}</option>}
          {options ? options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>) : children}
        </select>
        <span className="material-symbols-outlined" style={{
          position: "absolute", right: 12, fontSize: 20,
          color: "var(--on-surface-variant)", pointerEvents: "none",
        }}>expand_more</span>
      </div>
      {error && <span style={{ fontFamily: "var(--font-sans)", fontSize: 12, color: "var(--error)" }}>{error}</span>}
    </div>
  );
}
