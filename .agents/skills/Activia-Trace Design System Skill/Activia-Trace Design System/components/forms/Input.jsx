import React from "react";

/**
 * Input — text field with optional leading icon, label, and helper/error text.
 * Surface fill, hairline border, violet focus ring. Pill option for search bars.
 */
export function Input({
  label,
  icon,
  type = "text",
  placeholder,
  value,
  onChange,
  helper,
  error,
  pill = false,
  disabled = false,
  id,
  style,
  ...rest
}) {
  const [focused, setFocused] = React.useState(false);
  const inputId = id || React.useId();
  const borderColor = error ? "var(--error)" : focused ? "var(--primary)" : "var(--outline-variant)";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, width: "100%" }}>
      {label && (
        <label htmlFor={inputId} style={{
          fontFamily: "var(--font-sans)", fontSize: 12, fontWeight: 600,
          letterSpacing: "0.05em", textTransform: "uppercase",
          color: "var(--on-surface-variant)",
        }}>{label}</label>
      )}
      <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
        {icon && (
          <span className="material-symbols-outlined" style={{
            position: "absolute", left: 12, fontSize: 20,
            color: focused ? "var(--primary)" : "var(--outline)", pointerEvents: "none",
          }}>{icon}</span>
        )}
        <input
          id={inputId}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          style={{
            width: "100%",
            height: 40,
            padding: icon ? "0 14px 0 40px" : "0 14px",
            background: "var(--surface-container-low)",
            color: "var(--on-surface)",
            border: `1px solid ${borderColor}`,
            borderRadius: pill ? "var(--radius-full)" : "var(--radius-md)",
            fontFamily: "var(--font-sans)",
            fontSize: 14,
            outline: "none",
            boxShadow: focused && !error ? "0 0 0 2px color-mix(in srgb, var(--primary) 30%, transparent)" : "none",
            opacity: disabled ? 0.5 : 1,
            transition: "border-color .15s ease, box-shadow .15s ease",
            ...style,
          }}
          {...rest}
        />
      </div>
      {(helper || error) && (
        <span style={{
          fontFamily: "var(--font-sans)", fontSize: 12,
          color: error ? "var(--error)" : "var(--on-surface-variant)",
        }}>{error || helper}</span>
      )}
    </div>
  );
}
