import React from "react";

/**
 * Avatar — circular user image or initials fallback. Optional status ring
 * and presence dot. Sizes: xs, sm, md, lg.
 */
export function Avatar({ src, name = "", size = "md", ring = false, status, alt, style }) {
  const dims = { xs: 24, sm: 32, md: 40, lg: 56 };
  const px = dims[size] || 40;
  const initials = name.split(" ").map((w) => w[0]).filter(Boolean).slice(0, 2).join("").toUpperCase();
  const statusColors = { online: "var(--tertiary)", busy: "var(--error)", away: "#fbbf24", offline: "var(--outline)" };

  return (
    <span style={{ position: "relative", display: "inline-block", width: px, height: px, ...style }}>
      <span style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        width: px, height: px, borderRadius: "var(--radius-full)", overflow: "hidden",
        background: "var(--surface-container-highest)",
        color: "var(--on-surface-variant)",
        fontFamily: "var(--font-sans)", fontWeight: 700, fontSize: px * 0.36,
        border: ring ? "2px solid var(--primary)" : "1px solid var(--outline-variant)",
        boxSizing: "border-box",
      }}>
        {src ? <img src={src} alt={alt || name} style={{ width: "100%", height: "100%", objectFit: "cover" }} /> : initials}
      </span>
      {status && (
        <span style={{
          position: "absolute", bottom: 0, right: 0,
          width: px * 0.28, height: px * 0.28, minWidth: 8, minHeight: 8,
          borderRadius: "var(--radius-full)",
          background: statusColors[status] || statusColors.offline,
          border: "2px solid var(--background)",
        }} />
      )}
    </span>
  );
}
