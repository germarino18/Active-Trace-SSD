import React from "react";

/**
 * Tabs — horizontal tab bar with an underline indicator (the Materias layout
 * uses these for its 5 sub-views). Controlled via value/onChange.
 * tabs = [{ id, label, icon?, badge? }]
 */
export function Tabs({ tabs = [], value, onChange, style }) {
  return (
    <div role="tablist" style={{
      display: "flex", gap: 4, borderBottom: "1px solid var(--outline-variant)",
      overflowX: "auto", ...style,
    }}>
      {tabs.map((t) => {
        const active = t.id === value;
        return (
          <button
            key={t.id}
            role="tab"
            aria-selected={active}
            onClick={() => onChange && onChange(t.id)}
            style={{
              position: "relative",
              display: "inline-flex", alignItems: "center", gap: 8,
              padding: "12px 16px", background: "transparent", border: "none",
              borderBottom: active ? "2px solid var(--primary)" : "2px solid transparent",
              marginBottom: -1,
              fontFamily: "var(--font-sans)", fontSize: 14, fontWeight: 600,
              color: active ? "var(--primary)" : "var(--on-surface-variant)",
              cursor: "pointer", whiteSpace: "nowrap",
              transition: "color .15s ease",
            }}
            onMouseEnter={(e) => { if (!active) e.currentTarget.style.color = "var(--on-surface)"; }}
            onMouseLeave={(e) => { if (!active) e.currentTarget.style.color = "var(--on-surface-variant)"; }}
          >
            {t.icon && <span className="material-symbols-outlined" style={{ fontSize: 18 }}>{t.icon}</span>}
            {t.label}
            {t.badge != null && (
              <span style={{
                minWidth: 18, height: 18, padding: "0 5px", display: "inline-flex",
                alignItems: "center", justifyContent: "center",
                borderRadius: "var(--radius-full)", fontSize: 11, fontWeight: 700,
                background: active ? "color-mix(in srgb, var(--primary) 18%, transparent)" : "var(--surface-container-highest)",
                color: active ? "var(--primary)" : "var(--on-surface-variant)",
              }}>{t.badge}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
