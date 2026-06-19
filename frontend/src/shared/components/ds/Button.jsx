import React from "react";

/**
 * Button — primary action control for Activia-Trace.
 * Variants: primary (solid violet), secondary (outlined), tertiary (emerald),
 * ghost (text-only), danger. Sizes: sm, md, lg. Optional leading/trailing icon.
 */
export function Button({
  children,
  variant = "primary",
  size = "md",
  icon,
  trailingIcon,
  fullWidth = false,
  disabled = false,
  type = "button",
  onClick,
  style,
  ...rest
}) {
  const sizes = {
    sm: { padding: "0 12px", height: 32, font: 12, gap: 6, radius: "var(--radius-md)" },
    md: { padding: "0 16px", height: 40, font: 14, gap: 8, radius: "var(--radius-md)" },
    lg: { padding: "0 24px", height: 48, font: 15, gap: 8, radius: "var(--radius-lg)" },
  };
  const s = sizes[size] || sizes.md;

  const variants = {
    primary: {
      background: "var(--primary)",
      color: "var(--on-primary)",
      border: "1px solid transparent",
      boxShadow: "var(--shadow-primary)",
    },
    secondary: {
      background: "var(--surface-container-high)",
      color: "var(--on-surface)",
      border: "1px solid var(--outline-variant)",
    },
    tertiary: {
      background: "var(--tertiary)",
      color: "var(--on-tertiary)",
      border: "1px solid transparent",
    },
    ghost: {
      background: "transparent",
      color: "var(--on-surface-variant)",
      border: "1px solid transparent",
    },
    danger: {
      background: "var(--error-container)",
      color: "var(--on-error-container)",
      border: "1px solid color-mix(in srgb, var(--error) 30%, transparent)",
    },
  };
  const v = variants[variant] || variants.primary;

  const base = {
    display: fullWidth ? "flex" : "inline-flex",
    width: fullWidth ? "100%" : undefined,
    alignItems: "center",
    justifyContent: "center",
    gap: s.gap,
    height: s.height,
    padding: s.padding,
    borderRadius: s.radius,
    fontFamily: "var(--font-sans)",
    fontSize: s.font,
    fontWeight: 600,
    letterSpacing: "0.01em",
    lineHeight: 1,
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.45 : 1,
    whiteSpace: "nowrap",
    transition: "transform .12s ease, filter .15s ease, background .15s ease",
    userSelect: "none",
    ...v,
    ...style,
  };

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      style={base}
      onMouseDown={(e) => { if (!disabled) e.currentTarget.style.transform = "scale(0.97)"; }}
      onMouseUp={(e) => { e.currentTarget.style.transform = "scale(1)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.transform = "scale(1)"; e.currentTarget.style.filter = "none"; }}
      onMouseEnter={(e) => { if (!disabled) e.currentTarget.style.filter = "brightness(1.08)"; }}
      {...rest}
    >
      {icon && <span className="material-symbols-outlined" style={{ fontSize: s.font + 4 }}>{icon}</span>}
      {children}
      {trailingIcon && <span className="material-symbols-outlined" style={{ fontSize: s.font + 4 }}>{trailingIcon}</span>}
    </button>
  );
}
