import React from "react";

/**
 * IconButton — square, icon-only control (header actions, toolbars, row menus).
 * Variants: ghost (default), solid, outline. Optional violet "active" state and
 * a notification dot.
 */
export function IconButton({
  icon,
  size = "md",
  variant = "ghost",
  active = false,
  dot = false,
  disabled = false,
  label,
  onClick,
  style,
  ...rest
}) {
  const dims = { sm: 32, md: 40, lg: 44 };
  const px = dims[size] || 40;
  const glyph = { sm: 18, md: 20, lg: 24 };

  const variants = {
    ghost: { background: "transparent", border: "1px solid transparent" },
    solid: { background: "var(--surface-container-high)", border: "1px solid var(--outline-variant)" },
    outline: { background: "transparent", border: "1px solid var(--outline-variant)" },
  };
  const v = variants[variant] || variants.ghost;

  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      disabled={disabled}
      onClick={onClick}
      style={{
        position: "relative",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: px,
        height: px,
        borderRadius: "var(--radius-full)",
        color: active ? "var(--primary)" : "var(--on-surface-variant)",
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.45 : 1,
        transition: "color .15s ease, background .15s ease",
        ...v,
        ...style,
      }}
      onMouseEnter={(e) => { if (!disabled && !active) e.currentTarget.style.color = "var(--primary)"; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.color = "var(--on-surface-variant)"; }}
      {...rest}
    >
      <span className="material-symbols-outlined" style={{ fontSize: glyph[size] || 20 }}>{icon}</span>
      {dot && (
        <span style={{
          position: "absolute", top: 8, right: 8, width: 8, height: 8,
          borderRadius: "var(--radius-full)", background: "var(--error)",
          border: "2px solid var(--background)",
        }} />
      )}
    </button>
  );
}
