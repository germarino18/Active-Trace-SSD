import React from "react";

/**
 * Card — the base surface container. Hairline border, no shadow by default
 * (Obsidian uses borders for separation). variant="glass" adds backdrop blur.
 * Optional title/subtitle header and action slot.
 */
export function Card({ children, title, subtitle, action, icon, variant = "default", padding = 24, hover = false, style }) {
  const variants = {
    default: { background: "var(--surface-container)", border: "1px solid var(--outline-variant)" },
    low: { background: "var(--surface-container-low)", border: "1px solid var(--outline-variant)" },
    glass: { background: "var(--glass-bg)", backdropFilter: "blur(var(--glass-blur))", WebkitBackdropFilter: "blur(var(--glass-blur))", border: "1px solid var(--outline-variant)" },
  };
  const v = variants[variant] || variants.default;
  const [hovered, setHovered] = React.useState(false);

  return (
    <div
      onMouseEnter={() => hover && setHovered(true)}
      onMouseLeave={() => hover && setHovered(false)}
      style={{
        display: "flex", flexDirection: "column",
        borderRadius: "var(--radius-lg)",
        padding,
        transition: "background .2s ease, border-color .2s ease, transform .2s ease",
        transform: hovered ? "translateY(-2px)" : "none",
        borderColor: hovered ? "var(--outline)" : undefined,
        ...v,
        ...style,
      }}
    >
      {(title || action) && (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: subtitle ? 4 : 16, gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 0 }}>
            {icon && <span className="material-symbols-outlined" style={{ fontSize: 20, color: "var(--primary)" }}>{icon}</span>}
            <h3 style={{
              margin: 0, fontFamily: "var(--font-sans)", fontSize: 13, fontWeight: 700,
              letterSpacing: "0.05em", textTransform: "uppercase", color: "var(--on-surface-variant)",
            }}>{title}</h3>
          </div>
          {action}
        </div>
      )}
      {subtitle && <p style={{ margin: "0 0 16px", fontFamily: "var(--font-sans)", fontSize: 13, color: "var(--on-surface-variant)" }}>{subtitle}</p>}
      {children}
    </div>
  );
}
