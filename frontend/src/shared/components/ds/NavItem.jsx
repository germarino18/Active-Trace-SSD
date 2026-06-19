import React from "react";

/**
 * NavItem — sidebar navigation row. Active state = violet text on raised
 * surface with a right violet accent bar. Used in the app sidebar.
 */
export function NavItem({ icon, label, active = false, onClick, href = "#", badge, style }) {
  const [hover, setHover] = React.useState(false);
  return (
    <a
      href={href}
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: "flex", alignItems: "center", gap: 12,
        padding: "10px 12px",
        borderRadius: "var(--radius-md)",
        textDecoration: "none",
        fontFamily: "var(--font-sans)", fontSize: 14,
        fontWeight: active ? 700 : 500,
        color: active ? "var(--primary)" : "var(--on-surface-variant)",
        background: active ? "var(--surface-container-highest)" : hover ? "var(--surface-container-high)" : "transparent",
        borderRight: active ? "2px solid var(--primary)" : "2px solid transparent",
        transition: "background .15s ease, color .15s ease",
        cursor: "pointer",
        ...style,
      }}
    >
      <span className="material-symbols-outlined" style={{ fontSize: 20 }}>{icon}</span>
      <span style={{ flex: 1 }}>{label}</span>
      {badge != null && (
        <span style={{
          minWidth: 20, height: 20, padding: "0 6px", display: "inline-flex",
          alignItems: "center", justifyContent: "center",
          borderRadius: "var(--radius-full)", fontSize: 11, fontWeight: 700,
          background: "color-mix(in srgb, var(--primary) 18%, transparent)", color: "var(--primary)",
        }}>{badge}</span>
      )}
    </a>
  );
}
