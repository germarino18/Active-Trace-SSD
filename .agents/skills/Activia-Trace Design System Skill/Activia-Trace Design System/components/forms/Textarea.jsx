import React from "react";

/** Textarea — multi-line field, same surface/border/focus language as Input. */
export function Textarea({ label, placeholder, value, onChange, rows = 4, helper, error, disabled = false, id, style, ...rest }) {
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
      <textarea
        id={inputId}
        rows={rows}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          width: "100%",
          padding: "10px 14px",
          background: "var(--surface-container-low)",
          color: "var(--on-surface)",
          border: `1px solid ${borderColor}`,
          borderRadius: "var(--radius-md)",
          fontFamily: "var(--font-sans)",
          fontSize: 14,
          lineHeight: 1.5,
          resize: "vertical",
          outline: "none",
          boxShadow: focused && !error ? "0 0 0 2px color-mix(in srgb, var(--primary) 30%, transparent)" : "none",
          transition: "border-color .15s ease, box-shadow .15s ease",
          ...style,
        }}
        {...rest}
      />
      {(helper || error) && (
        <span style={{ fontFamily: "var(--font-sans)", fontSize: 12, color: error ? "var(--error)" : "var(--on-surface-variant)" }}>{error || helper}</span>
      )}
    </div>
  );
}
