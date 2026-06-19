/* @ds-bundle: {"format":3,"namespace":"ActiviaTraceDesignSystem_944743","components":[{"name":"Avatar","sourcePath":"components/display/Avatar.jsx"},{"name":"Badge","sourcePath":"components/display/Badge.jsx"},{"name":"Card","sourcePath":"components/display/Card.jsx"},{"name":"ProgressBar","sourcePath":"components/display/ProgressBar.jsx"},{"name":"StatCard","sourcePath":"components/display/StatCard.jsx"},{"name":"Tag","sourcePath":"components/display/Tag.jsx"},{"name":"EmptyState","sourcePath":"components/feedback/EmptyState.jsx"},{"name":"Button","sourcePath":"components/forms/Button.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"IconButton","sourcePath":"components/forms/IconButton.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"},{"name":"Textarea","sourcePath":"components/forms/Textarea.jsx"},{"name":"NavItem","sourcePath":"components/navigation/NavItem.jsx"},{"name":"Tabs","sourcePath":"components/navigation/Tabs.jsx"}],"sourceHashes":{"components/display/Avatar.jsx":"86f7679e9789","components/display/Badge.jsx":"198341de56d2","components/display/Card.jsx":"870a3baff44b","components/display/ProgressBar.jsx":"e030a1311fe0","components/display/StatCard.jsx":"1a75070b11b6","components/display/Tag.jsx":"902c4d99f803","components/feedback/EmptyState.jsx":"aa8614235b77","components/forms/Button.jsx":"034145495320","components/forms/Checkbox.jsx":"53685be39364","components/forms/IconButton.jsx":"d53ef5608f7e","components/forms/Input.jsx":"a04bc37c29ac","components/forms/Select.jsx":"985f0637ae98","components/forms/Switch.jsx":"1dd4bd8edbb2","components/forms/Textarea.jsx":"4495daf616b7","components/navigation/NavItem.jsx":"c1da1be7c860","components/navigation/Tabs.jsx":"3890cb3b791b","ui_kits/activia-trace/App.jsx":"4d5b41289d55","ui_kits/activia-trace/AppShell.jsx":"2ab4faa29878","ui_kits/activia-trace/DashboardScreen.jsx":"0e0ce6aa6867","ui_kits/activia-trace/LoginScreen.jsx":"b4be0b89b59c","ui_kits/activia-trace/MateriaTabs.jsx":"335faa4e755d","ui_kits/activia-trace/MateriasScreen.jsx":"ee2590e4cb5f","ui_kits/activia-trace/ProfileScreen.jsx":"fdd71eb0f66b"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.ActiviaTraceDesignSystem_944743 = window.ActiviaTraceDesignSystem_944743 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/display/Avatar.jsx
try { (() => {
/**
 * Avatar — circular user image or initials fallback. Optional status ring
 * and presence dot. Sizes: xs, sm, md, lg.
 */
function Avatar({
  src,
  name = "",
  size = "md",
  ring = false,
  status,
  alt,
  style
}) {
  const dims = {
    xs: 24,
    sm: 32,
    md: 40,
    lg: 56
  };
  const px = dims[size] || 40;
  const initials = name.split(" ").map(w => w[0]).filter(Boolean).slice(0, 2).join("").toUpperCase();
  const statusColors = {
    online: "var(--tertiary)",
    busy: "var(--error)",
    away: "#fbbf24",
    offline: "var(--outline)"
  };
  return /*#__PURE__*/React.createElement("span", {
    style: {
      position: "relative",
      display: "inline-block",
      width: px,
      height: px,
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      width: px,
      height: px,
      borderRadius: "var(--radius-full)",
      overflow: "hidden",
      background: "var(--surface-container-highest)",
      color: "var(--on-surface-variant)",
      fontFamily: "var(--font-sans)",
      fontWeight: 700,
      fontSize: px * 0.36,
      border: ring ? "2px solid var(--primary)" : "1px solid var(--outline-variant)",
      boxSizing: "border-box"
    }
  }, src ? /*#__PURE__*/React.createElement("img", {
    src: src,
    alt: alt || name,
    style: {
      width: "100%",
      height: "100%",
      objectFit: "cover"
    }
  }) : initials), status && /*#__PURE__*/React.createElement("span", {
    style: {
      position: "absolute",
      bottom: 0,
      right: 0,
      width: px * 0.28,
      height: px * 0.28,
      minWidth: 8,
      minHeight: 8,
      borderRadius: "var(--radius-full)",
      background: statusColors[status] || statusColors.offline,
      border: "2px solid var(--background)"
    }
  }));
}
Object.assign(__ds_scope, { Avatar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Avatar.jsx", error: String((e && e.message) || e) }); }

// components/display/Badge.jsx
try { (() => {
/**
 * Badge — small status pill. Tones: primary, success, danger, neutral, warning.
 * Style: "soft" (tinted bg + colored text, default) or "solid". Optional dot.
 */
function Badge({
  children,
  tone = "neutral",
  variant = "soft",
  dot = false,
  icon,
  style
}) {
  const tones = {
    primary: {
      fg: "var(--primary)",
      solidBg: "var(--primary)",
      solidFg: "var(--on-primary)"
    },
    success: {
      fg: "var(--tertiary)",
      solidBg: "var(--tertiary)",
      solidFg: "var(--on-tertiary)"
    },
    danger: {
      fg: "var(--error)",
      solidBg: "var(--error)",
      solidFg: "var(--on-error)"
    },
    warning: {
      fg: "#fbbf24",
      solidBg: "#fbbf24",
      solidFg: "#1a1200"
    },
    neutral: {
      fg: "var(--on-surface-variant)",
      solidBg: "var(--secondary-container)",
      solidFg: "var(--on-surface)"
    }
  };
  const t = tones[tone] || tones.neutral;
  const soft = {
    background: `color-mix(in srgb, ${t.fg} 14%, transparent)`,
    color: t.fg,
    border: `1px solid color-mix(in srgb, ${t.fg} 28%, transparent)`
  };
  const solid = {
    background: t.solidBg,
    color: t.solidFg,
    border: "1px solid transparent"
  };
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      height: 22,
      padding: "0 10px",
      borderRadius: "var(--radius-full)",
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 600,
      letterSpacing: "0.02em",
      lineHeight: 1,
      whiteSpace: "nowrap",
      ...(variant === "solid" ? solid : soft),
      ...style
    }
  }, dot && /*#__PURE__*/React.createElement("span", {
    style: {
      width: 6,
      height: 6,
      borderRadius: "var(--radius-full)",
      background: "currentColor"
    }
  }), icon && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 14
    }
  }, icon), children);
}
Object.assign(__ds_scope, { Badge });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Badge.jsx", error: String((e && e.message) || e) }); }

// components/display/Card.jsx
try { (() => {
/**
 * Card — the base surface container. Hairline border, no shadow by default
 * (Obsidian uses borders for separation). variant="glass" adds backdrop blur.
 * Optional title/subtitle header and action slot.
 */
function Card({
  children,
  title,
  subtitle,
  action,
  icon,
  variant = "default",
  padding = 24,
  hover = false,
  style
}) {
  const variants = {
    default: {
      background: "var(--surface-container)",
      border: "1px solid var(--outline-variant)"
    },
    low: {
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)"
    },
    glass: {
      background: "var(--glass-bg)",
      backdropFilter: "blur(var(--glass-blur))",
      WebkitBackdropFilter: "blur(var(--glass-blur))",
      border: "1px solid var(--outline-variant)"
    }
  };
  const v = variants[variant] || variants.default;
  const [hovered, setHovered] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", {
    onMouseEnter: () => hover && setHovered(true),
    onMouseLeave: () => hover && setHovered(false),
    style: {
      display: "flex",
      flexDirection: "column",
      borderRadius: "var(--radius-lg)",
      padding,
      transition: "background .2s ease, border-color .2s ease, transform .2s ease",
      transform: hovered ? "translateY(-2px)" : "none",
      borderColor: hovered ? "var(--outline)" : undefined,
      ...v,
      ...style
    }
  }, (title || action) && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: subtitle ? 4 : 16,
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      minWidth: 0
    }
  }, icon && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 20,
      color: "var(--primary)"
    }
  }, icon), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontFamily: "var(--font-sans)",
      fontSize: 13,
      fontWeight: 700,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)"
    }
  }, title)), action), subtitle && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "0 0 16px",
      fontFamily: "var(--font-sans)",
      fontSize: 13,
      color: "var(--on-surface-variant)"
    }
  }, subtitle), children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Card.jsx", error: String((e && e.message) || e) }); }

// components/display/ProgressBar.jsx
try { (() => {
/** ProgressBar — thin track. Tones: primary, success. Optional segmented mode. */
function ProgressBar({
  value = 0,
  tone = "primary",
  height = 8,
  label,
  showValue = false,
  segments,
  style
}) {
  const color = tone === "success" ? "var(--tertiary)" : "var(--primary)";
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 6,
      width: "100%",
      ...style
    }
  }, (label || showValue) && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      fontWeight: 600,
      letterSpacing: "0.04em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)"
    }
  }, label && /*#__PURE__*/React.createElement("span", null, label), showValue && /*#__PURE__*/React.createElement("span", null, Math.round(value), "%")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      width: "100%",
      height,
      borderRadius: "var(--radius-full)",
      background: "var(--surface-container-highest)",
      overflow: "hidden"
    }
  }, segments ? segments.map((seg, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      width: `${seg.value}%`,
      height: "100%",
      background: seg.color || color
    }
  })) : /*#__PURE__*/React.createElement("div", {
    style: {
      width: `${Math.min(100, Math.max(0, value))}%`,
      height: "100%",
      background: color,
      borderRadius: "var(--radius-full)",
      transition: "width 1s ease"
    }
  })));
}
Object.assign(__ds_scope, { ProgressBar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/ProgressBar.jsx", error: String((e && e.message) || e) }); }

// components/display/StatCard.jsx
try { (() => {
/**
 * StatCard — KPI tile. Big number, label, optional trend + progress bar.
 * tone="primary" renders the filled violet highlight variant.
 */
function StatCard({
  label,
  value,
  unit,
  trend,
  trendDir = "up",
  icon,
  progress,
  tone = "default",
  style
}) {
  const filled = tone === "primary";
  const trendColor = trendDir === "down" ? "var(--error)" : "var(--tertiary)";
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      gap: 16,
      minHeight: 130,
      padding: 24,
      borderRadius: "var(--radius-lg)",
      background: filled ? "var(--primary-container)" : "var(--surface-container)",
      color: filled ? "var(--on-primary-container)" : "var(--on-surface)",
      border: filled ? "1px solid color-mix(in srgb, var(--primary) 25%, transparent)" : "1px solid var(--outline-variant)",
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 11,
      fontWeight: 600,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: filled ? "color-mix(in srgb, var(--on-primary-container) 80%, transparent)" : "var(--on-surface-variant)"
    }
  }, label), icon && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 20,
      color: filled ? "var(--on-primary-container)" : "var(--primary)"
    }
  }, icon)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "baseline",
      gap: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 36,
      fontWeight: 800,
      letterSpacing: "-0.02em",
      lineHeight: 1
    }
  }, value), unit && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 16,
      fontWeight: 600,
      opacity: 0.5
    }
  }, unit)), trend && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 4,
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 500,
      color: filled ? "inherit" : trendColor
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 16
    }
  }, trendDir === "down" ? "trending_down" : "trending_up"), trend), typeof progress === "number" && /*#__PURE__*/React.createElement("div", {
    style: {
      width: "100%",
      height: 6,
      borderRadius: "var(--radius-full)",
      background: filled ? "color-mix(in srgb, var(--on-primary-container) 20%, transparent)" : "var(--surface-container-highest)",
      overflow: "hidden"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: `${Math.min(100, Math.max(0, progress))}%`,
      height: "100%",
      background: filled ? "var(--on-primary-container)" : "var(--tertiary)",
      borderRadius: "var(--radius-full)"
    }
  })));
}
Object.assign(__ds_scope, { StatCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/StatCard.jsx", error: String((e && e.message) || e) }); }

// components/display/Tag.jsx
try { (() => {
/** Tag — low-emphasis metadata chip (subject codes, filters, categories). */
function Tag({
  children,
  icon,
  onRemove,
  style
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      height: 24,
      padding: "0 8px",
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-sm)",
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 500,
      color: "var(--on-surface-variant)",
      whiteSpace: "nowrap",
      ...style
    }
  }, icon && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 14
    }
  }, icon), children, onRemove && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    onClick: onRemove,
    style: {
      fontSize: 14,
      cursor: "pointer",
      marginLeft: 2
    }
  }, "close"));
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/display/Tag.jsx", error: String((e && e.message) || e) }); }

// components/feedback/EmptyState.jsx
try { (() => {
/**
 * EmptyState — centered placeholder for empty tables, error screens (403/404),
 * and "no results" views. Icon in a tinted circle, title, message, optional action.
 */
function EmptyState({
  icon = "inbox",
  title,
  message,
  action,
  code,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      textAlign: "center",
      padding: 48,
      gap: 8,
      ...style
    }
  }, code ? /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 72,
      fontWeight: 800,
      letterSpacing: "-0.04em",
      lineHeight: 1,
      color: "var(--primary)"
    }
  }, code) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      width: 64,
      height: 64,
      borderRadius: "var(--radius-full)",
      background: "color-mix(in srgb, var(--primary) 12%, transparent)",
      color: "var(--primary)",
      marginBottom: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 32
    }
  }, icon)), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontFamily: "var(--font-sans)",
      fontSize: 20,
      fontWeight: 700,
      color: "var(--on-surface)"
    }
  }, title), message && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      maxWidth: 420,
      fontFamily: "var(--font-sans)",
      fontSize: 14,
      lineHeight: 1.5,
      color: "var(--on-surface-variant)"
    }
  }, message), action && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 16
    }
  }, action));
}
Object.assign(__ds_scope, { EmptyState });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/EmptyState.jsx", error: String((e && e.message) || e) }); }

// components/forms/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Button — primary action control for Activia-Trace.
 * Variants: primary (solid violet), secondary (outlined), tertiary (emerald),
 * ghost (text-only), danger. Sizes: sm, md, lg. Optional leading/trailing icon.
 */
function Button({
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
    sm: {
      padding: "0 12px",
      height: 32,
      font: 12,
      gap: 6,
      radius: "var(--radius-md)"
    },
    md: {
      padding: "0 16px",
      height: 40,
      font: 14,
      gap: 8,
      radius: "var(--radius-md)"
    },
    lg: {
      padding: "0 24px",
      height: 48,
      font: 15,
      gap: 8,
      radius: "var(--radius-lg)"
    }
  };
  const s = sizes[size] || sizes.md;
  const variants = {
    primary: {
      background: "var(--primary)",
      color: "var(--on-primary)",
      border: "1px solid transparent",
      boxShadow: "var(--shadow-primary)"
    },
    secondary: {
      background: "var(--surface-container-high)",
      color: "var(--on-surface)",
      border: "1px solid var(--outline-variant)"
    },
    tertiary: {
      background: "var(--tertiary)",
      color: "var(--on-tertiary)",
      border: "1px solid transparent"
    },
    ghost: {
      background: "transparent",
      color: "var(--on-surface-variant)",
      border: "1px solid transparent"
    },
    danger: {
      background: "var(--error-container)",
      color: "var(--on-error-container)",
      border: "1px solid color-mix(in srgb, var(--error) 30%, transparent)"
    }
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
    ...style
  };
  return /*#__PURE__*/React.createElement("button", _extends({
    type: type,
    disabled: disabled,
    onClick: onClick,
    style: base,
    onMouseDown: e => {
      if (!disabled) e.currentTarget.style.transform = "scale(0.97)";
    },
    onMouseUp: e => {
      e.currentTarget.style.transform = "scale(1)";
    },
    onMouseLeave: e => {
      e.currentTarget.style.transform = "scale(1)";
      e.currentTarget.style.filter = "none";
    },
    onMouseEnter: e => {
      if (!disabled) e.currentTarget.style.filter = "brightness(1.08)";
    }
  }, rest), icon && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: s.font + 4
    }
  }, icon), children, trailingIcon && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: s.font + 4
    }
  }, trailingIcon));
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Button.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
/** Checkbox — square check with violet fill when selected. */
function Checkbox({
  checked = false,
  onChange,
  disabled = false,
  label,
  id
}) {
  const inputId = id || React.useId();
  return /*#__PURE__*/React.createElement("label", {
    htmlFor: inputId,
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.5 : 1
    }
  }, /*#__PURE__*/React.createElement("button", {
    id: inputId,
    type: "button",
    role: "checkbox",
    "aria-checked": checked,
    disabled: disabled,
    onClick: () => !disabled && onChange && onChange(!checked),
    style: {
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      width: 18,
      height: 18,
      flexShrink: 0,
      padding: 0,
      borderRadius: "var(--radius-sm)",
      background: checked ? "var(--primary)" : "var(--surface-container-low)",
      border: checked ? "1px solid var(--primary)" : "1px solid var(--outline)",
      cursor: disabled ? "not-allowed" : "pointer",
      transition: "background .15s ease, border-color .15s ease"
    }
  }, checked && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 16,
      color: "var(--on-primary)"
    }
  }, "check")), label && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 14,
      color: "var(--on-surface)"
    }
  }, label));
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * IconButton — square, icon-only control (header actions, toolbars, row menus).
 * Variants: ghost (default), solid, outline. Optional violet "active" state and
 * a notification dot.
 */
function IconButton({
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
  const dims = {
    sm: 32,
    md: 40,
    lg: 44
  };
  const px = dims[size] || 40;
  const glyph = {
    sm: 18,
    md: 20,
    lg: 24
  };
  const variants = {
    ghost: {
      background: "transparent",
      border: "1px solid transparent"
    },
    solid: {
      background: "var(--surface-container-high)",
      border: "1px solid var(--outline-variant)"
    },
    outline: {
      background: "transparent",
      border: "1px solid var(--outline-variant)"
    }
  };
  const v = variants[variant] || variants.ghost;
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    "aria-label": label,
    title: label,
    disabled: disabled,
    onClick: onClick,
    style: {
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
      ...style
    },
    onMouseEnter: e => {
      if (!disabled && !active) e.currentTarget.style.color = "var(--primary)";
    },
    onMouseLeave: e => {
      if (!active) e.currentTarget.style.color = "var(--on-surface-variant)";
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: glyph[size] || 20
    }
  }, icon), dot && /*#__PURE__*/React.createElement("span", {
    style: {
      position: "absolute",
      top: 8,
      right: 8,
      width: 8,
      height: 8,
      borderRadius: "var(--radius-full)",
      background: "var(--error)",
      border: "2px solid var(--background)"
    }
  }));
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Input — text field with optional leading icon, label, and helper/error text.
 * Surface fill, hairline border, violet focus ring. Pill option for search bars.
 */
function Input({
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
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 6,
      width: "100%"
    }
  }, label && /*#__PURE__*/React.createElement("label", {
    htmlFor: inputId,
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 600,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)"
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      display: "flex",
      alignItems: "center"
    }
  }, icon && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      position: "absolute",
      left: 12,
      fontSize: 20,
      color: focused ? "var(--primary)" : "var(--outline)",
      pointerEvents: "none"
    }
  }, icon), /*#__PURE__*/React.createElement("input", _extends({
    id: inputId,
    type: type,
    placeholder: placeholder,
    value: value,
    onChange: onChange,
    disabled: disabled,
    onFocus: () => setFocused(true),
    onBlur: () => setFocused(false),
    style: {
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
      ...style
    }
  }, rest))), (helper || error) && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      color: error ? "var(--error)" : "var(--on-surface-variant)"
    }
  }, error || helper));
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Select — native dropdown styled to match Input. Pass options=[{value,label}] or children. */
function Select({
  label,
  value,
  onChange,
  options,
  children,
  placeholder,
  disabled = false,
  error,
  id,
  style,
  ...rest
}) {
  const [focused, setFocused] = React.useState(false);
  const inputId = id || React.useId();
  const borderColor = error ? "var(--error)" : focused ? "var(--primary)" : "var(--outline-variant)";
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 6,
      width: "100%"
    }
  }, label && /*#__PURE__*/React.createElement("label", {
    htmlFor: inputId,
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 600,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)"
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      display: "flex",
      alignItems: "center"
    }
  }, /*#__PURE__*/React.createElement("select", _extends({
    id: inputId,
    value: value,
    onChange: onChange,
    disabled: disabled,
    onFocus: () => setFocused(true),
    onBlur: () => setFocused(false),
    style: {
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
      ...style
    }
  }, rest), placeholder && /*#__PURE__*/React.createElement("option", {
    value: "",
    disabled: true
  }, placeholder), options ? options.map(o => /*#__PURE__*/React.createElement("option", {
    key: o.value,
    value: o.value
  }, o.label)) : children), /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      position: "absolute",
      right: 12,
      fontSize: 20,
      color: "var(--on-surface-variant)",
      pointerEvents: "none"
    }
  }, "expand_more")), error && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      color: "var(--error)"
    }
  }, error));
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
/** Switch — Material-style toggle. On = violet track, knob slides right. */
function Switch({
  checked = false,
  onChange,
  disabled = false,
  label,
  id
}) {
  const inputId = id || React.useId();
  return /*#__PURE__*/React.createElement("label", {
    htmlFor: inputId,
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      cursor: disabled ? "not-allowed" : "pointer",
      opacity: disabled ? 0.5 : 1
    }
  }, /*#__PURE__*/React.createElement("button", {
    id: inputId,
    type: "button",
    role: "switch",
    "aria-checked": checked,
    disabled: disabled,
    onClick: () => !disabled && onChange && onChange(!checked),
    style: {
      position: "relative",
      width: 40,
      height: 20,
      flexShrink: 0,
      borderRadius: "var(--radius-full)",
      background: checked ? "var(--primary)" : "var(--surface-container-highest)",
      border: checked ? "1px solid transparent" : "1px solid var(--outline-variant)",
      cursor: disabled ? "not-allowed" : "pointer",
      transition: "background .2s ease",
      padding: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: "absolute",
      top: 2,
      left: 2,
      width: 16,
      height: 16,
      borderRadius: "var(--radius-full)",
      background: checked ? "var(--on-primary)" : "var(--on-surface-variant)",
      transform: checked ? "translateX(20px)" : "translateX(0)",
      transition: "transform .2s ease"
    }
  })), label && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 14,
      color: "var(--on-surface)"
    }
  }, label));
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// components/forms/Textarea.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/** Textarea — multi-line field, same surface/border/focus language as Input. */
function Textarea({
  label,
  placeholder,
  value,
  onChange,
  rows = 4,
  helper,
  error,
  disabled = false,
  id,
  style,
  ...rest
}) {
  const [focused, setFocused] = React.useState(false);
  const inputId = id || React.useId();
  const borderColor = error ? "var(--error)" : focused ? "var(--primary)" : "var(--outline-variant)";
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 6,
      width: "100%"
    }
  }, label && /*#__PURE__*/React.createElement("label", {
    htmlFor: inputId,
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      fontWeight: 600,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)"
    }
  }, label), /*#__PURE__*/React.createElement("textarea", _extends({
    id: inputId,
    rows: rows,
    placeholder: placeholder,
    value: value,
    onChange: onChange,
    disabled: disabled,
    onFocus: () => setFocused(true),
    onBlur: () => setFocused(false),
    style: {
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
      ...style
    }
  }, rest)), (helper || error) && /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-sans)",
      fontSize: 12,
      color: error ? "var(--error)" : "var(--on-surface-variant)"
    }
  }, error || helper));
}
Object.assign(__ds_scope, { Textarea });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Textarea.jsx", error: String((e && e.message) || e) }); }

// components/navigation/NavItem.jsx
try { (() => {
/**
 * NavItem — sidebar navigation row. Active state = violet text on raised
 * surface with a right violet accent bar. Used in the app sidebar.
 */
function NavItem({
  icon,
  label,
  active = false,
  onClick,
  href = "#",
  badge,
  style
}) {
  const [hover, setHover] = React.useState(false);
  return /*#__PURE__*/React.createElement("a", {
    href: href,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: "10px 12px",
      borderRadius: "var(--radius-md)",
      textDecoration: "none",
      fontFamily: "var(--font-sans)",
      fontSize: 14,
      fontWeight: active ? 700 : 500,
      color: active ? "var(--primary)" : "var(--on-surface-variant)",
      background: active ? "var(--surface-container-highest)" : hover ? "var(--surface-container-high)" : "transparent",
      borderRight: active ? "2px solid var(--primary)" : "2px solid transparent",
      transition: "background .15s ease, color .15s ease",
      cursor: "pointer",
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 20
    }
  }, icon), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1
    }
  }, label), badge != null && /*#__PURE__*/React.createElement("span", {
    style: {
      minWidth: 20,
      height: 20,
      padding: "0 6px",
      display: "inline-flex",
      alignItems: "center",
      justifyContent: "center",
      borderRadius: "var(--radius-full)",
      fontSize: 11,
      fontWeight: 700,
      background: "color-mix(in srgb, var(--primary) 18%, transparent)",
      color: "var(--primary)"
    }
  }, badge));
}
Object.assign(__ds_scope, { NavItem });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/NavItem.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tabs.jsx
try { (() => {
/**
 * Tabs — horizontal tab bar with an underline indicator (the Materias layout
 * uses these for its 5 sub-views). Controlled via value/onChange.
 * tabs = [{ id, label, icon?, badge? }]
 */
function Tabs({
  tabs = [],
  value,
  onChange,
  style
}) {
  return /*#__PURE__*/React.createElement("div", {
    role: "tablist",
    style: {
      display: "flex",
      gap: 4,
      borderBottom: "1px solid var(--outline-variant)",
      overflowX: "auto",
      ...style
    }
  }, tabs.map(t => {
    const active = t.id === value;
    return /*#__PURE__*/React.createElement("button", {
      key: t.id,
      role: "tab",
      "aria-selected": active,
      onClick: () => onChange && onChange(t.id),
      style: {
        position: "relative",
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        padding: "12px 16px",
        background: "transparent",
        border: "none",
        borderBottom: active ? "2px solid var(--primary)" : "2px solid transparent",
        marginBottom: -1,
        fontFamily: "var(--font-sans)",
        fontSize: 14,
        fontWeight: 600,
        color: active ? "var(--primary)" : "var(--on-surface-variant)",
        cursor: "pointer",
        whiteSpace: "nowrap",
        transition: "color .15s ease"
      },
      onMouseEnter: e => {
        if (!active) e.currentTarget.style.color = "var(--on-surface)";
      },
      onMouseLeave: e => {
        if (!active) e.currentTarget.style.color = "var(--on-surface-variant)";
      }
    }, t.icon && /*#__PURE__*/React.createElement("span", {
      className: "material-symbols-outlined",
      style: {
        fontSize: 18
      }
    }, t.icon), t.label, t.badge != null && /*#__PURE__*/React.createElement("span", {
      style: {
        minWidth: 18,
        height: 18,
        padding: "0 5px",
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "var(--radius-full)",
        fontSize: 11,
        fontWeight: 700,
        background: active ? "color-mix(in srgb, var(--primary) 18%, transparent)" : "var(--surface-container-highest)",
        color: active ? "var(--primary)" : "var(--on-surface-variant)"
      }
    }, t.badge));
  }));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tabs.jsx", error: String((e && e.message) || e) }); }

// ui_kits/activia-trace/App.jsx
try { (() => {
// App — orchestrates auth + routing across the Activia-Trace screens.
const {
  AppShell,
  LoginScreen,
  DashboardScreen,
  MateriasScreen,
  ProfileScreen,
  ErrorScreen
} = window;
function App() {
  const [authed, setAuthed] = React.useState(false);
  const [route, setRoute] = React.useState("dashboard");
  const [materia, setMateria] = React.useState(null);
  if (!authed) return /*#__PURE__*/React.createElement(LoginScreen, {
    onLogin: () => setAuthed(true)
  });
  const crumbs = {
    dashboard: ["Activia-Trace", "Dashboard"],
    materias: materia ? ["Activia-Trace", "Mis Materias", materia] : ["Activia-Trace", "Mis Materias"],
    profile: ["Activia-Trace", "Mi Perfil"],
    "403": ["Activia-Trace", "Error 403"],
    "404": ["Activia-Trace", "Error 404"]
  };
  const navigate = r => {
    setRoute(r);
    if (r !== "materias") setMateria(null);
  };
  return /*#__PURE__*/React.createElement(AppShell, {
    route: route,
    onNavigate: navigate,
    onLogout: () => {
      setAuthed(false);
      setRoute("dashboard");
      setMateria(null);
    },
    breadcrumb: crumbs[route]
  }, route === "dashboard" && /*#__PURE__*/React.createElement(DashboardScreen, {
    onOpenMaterias: () => navigate("materias")
  }), route === "materias" && /*#__PURE__*/React.createElement(MateriasScreen, {
    selected: materia,
    onSelect: setMateria,
    onBack: () => setMateria(null)
  }), route === "profile" && /*#__PURE__*/React.createElement(ProfileScreen, null), route === "403" && /*#__PURE__*/React.createElement(ErrorScreen, {
    code: "403",
    onHome: () => navigate("dashboard")
  }), route === "404" && /*#__PURE__*/React.createElement(ErrorScreen, {
    code: "404",
    onHome: () => navigate("dashboard")
  }));
}
ReactDOM.createRoot(document.getElementById("root")).render(/*#__PURE__*/React.createElement(App, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/activia-trace/App.jsx", error: String((e && e.message) || e) }); }

// ui_kits/activia-trace/AppShell.jsx
try { (() => {
// AppShell — sidebar + top header layout reused across every post-login screen.
const {
  NavItem,
  IconButton,
  Avatar,
  Button,
  Input
} = window.ActiviaTraceDesignSystem_944743;
function Sidebar({
  route,
  onNavigate,
  onLogout
}) {
  return /*#__PURE__*/React.createElement("aside", {
    style: {
      position: "fixed",
      left: 0,
      top: 0,
      height: "100vh",
      width: 256,
      background: "var(--surface-container)",
      borderRight: "1px solid var(--outline-variant)",
      display: "flex",
      flexDirection: "column",
      padding: "24px 16px",
      zIndex: 50,
      boxSizing: "border-box"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: "0 8px",
      marginBottom: 32
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 36,
      height: 36,
      background: "var(--primary)",
      borderRadius: "var(--radius-md)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "var(--on-primary)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 22,
      fontVariationSettings: "'FILL' 1"
    }
  }, "analytics")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 17,
      fontWeight: 700,
      letterSpacing: "-0.02em",
      color: "var(--on-surface)"
    }
  }, "Activia-Trace"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 9,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)",
      opacity: 0.6
    }
  }, "Academic Management"))), /*#__PURE__*/React.createElement("nav", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 4,
      flex: 1
    }
  }, /*#__PURE__*/React.createElement(NavItem, {
    icon: "dashboard",
    label: "Dashboard",
    active: route === "dashboard",
    onClick: e => {
      e.preventDefault();
      onNavigate("dashboard");
    }
  }), /*#__PURE__*/React.createElement(NavItem, {
    icon: "menu_book",
    label: "Mis Materias",
    badge: "6",
    active: route === "materias",
    onClick: e => {
      e.preventDefault();
      onNavigate("materias");
    }
  }), /*#__PURE__*/React.createElement(NavItem, {
    icon: "person",
    label: "Mi Perfil",
    active: route === "profile",
    onClick: e => {
      e.preventDefault();
      onNavigate("profile");
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 1,
      background: "var(--outline-variant)",
      margin: "8px 12px"
    }
  }), /*#__PURE__*/React.createElement(NavItem, {
    icon: "lock",
    label: "Demo \xB7 403",
    active: route === "403",
    onClick: e => {
      e.preventDefault();
      onNavigate("403");
    }
  }), /*#__PURE__*/React.createElement(NavItem, {
    icon: "error",
    label: "Demo \xB7 404",
    active: route === "404",
    onClick: e => {
      e.preventDefault();
      onNavigate("404");
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: "auto",
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    icon: "add",
    fullWidth: true
  }, "Nueva Materia"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10,
      padding: "0 4px"
    }
  }, /*#__PURE__*/React.createElement(Avatar, {
    name: "Elena Vance",
    status: "online",
    size: "sm"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      fontWeight: 700,
      color: "var(--on-surface)",
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis"
    }
  }, "Dra. Elena Vance"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 10,
      color: "var(--on-surface-variant)"
    }
  }, "Docente")), /*#__PURE__*/React.createElement(IconButton, {
    icon: "logout",
    size: "sm",
    label: "Cerrar sesi\xF3n",
    onClick: onLogout
  }))));
}
function TopHeader({
  breadcrumb = []
}) {
  return /*#__PURE__*/React.createElement("header", {
    style: {
      position: "sticky",
      top: 0,
      zIndex: 40,
      height: 64,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 24px",
      background: "var(--glass-bg)",
      backdropFilter: "blur(12px)",
      WebkitBackdropFilter: "blur(12px)",
      borderBottom: "1px solid var(--outline-variant)"
    }
  }, /*#__PURE__*/React.createElement("nav", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      fontSize: 13
    }
  }, breadcrumb.map((b, i) => /*#__PURE__*/React.createElement(React.Fragment, {
    key: i
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: i === breadcrumb.length - 1 ? "var(--on-surface)" : "var(--on-surface-variant)",
      fontWeight: i === breadcrumb.length - 1 ? 600 : 400
    }
  }, b), i < breadcrumb.length - 1 && /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 16,
      color: "var(--outline)"
    }
  }, "chevron_right")))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 240
    }
  }, /*#__PURE__*/React.createElement(Input, {
    pill: true,
    icon: "search",
    placeholder: "Buscar..."
  })), /*#__PURE__*/React.createElement(IconButton, {
    icon: "notifications",
    dot: true,
    label: "Notificaciones"
  }), /*#__PURE__*/React.createElement(IconButton, {
    icon: "help",
    label: "Ayuda"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      width: 1,
      height: 28,
      background: "var(--outline-variant)",
      margin: "0 4px"
    }
  }), /*#__PURE__*/React.createElement(Avatar, {
    name: "Elena Vance",
    ring: true,
    size: "sm"
  })));
}
function AppShell({
  route,
  onNavigate,
  onLogout,
  breadcrumb,
  children
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      minHeight: "100vh",
      background: "var(--background)"
    }
  }, /*#__PURE__*/React.createElement(Sidebar, {
    route: route,
    onNavigate: onNavigate,
    onLogout: onLogout
  }), /*#__PURE__*/React.createElement("main", {
    style: {
      marginLeft: 256,
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column"
    }
  }, /*#__PURE__*/React.createElement(TopHeader, {
    breadcrumb: breadcrumb
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 24,
      flex: 1
    }
  }, children)));
}
Object.assign(window, {
  AppShell
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/activia-trace/AppShell.jsx", error: String((e && e.message) || e) }); }

// ui_kits/activia-trace/DashboardScreen.jsx
try { (() => {
// DashboardScreen — welcome summary: stat tiles, cursos activos, notificaciones.
const {
  Card,
  StatCard,
  Badge,
  ProgressBar,
  Button
} = window.ActiviaTraceDesignSystem_944743;
function DashboardScreen({
  onOpenMaterias
}) {
  const cursos = [{
    code: "CS-402",
    name: "Algoritmos Avanzados",
    comision: "Comisión A",
    alumnos: 48,
    prog: 78,
    tone: "primary"
  }, {
    code: "DS-301",
    name: "Sistemas Distribuidos",
    comision: "Comisión B",
    alumnos: 56,
    prog: 42,
    tone: "tertiary"
  }, {
    code: "MAT-102",
    name: "Lógica y Matemática",
    comision: "Comisión C",
    alumnos: 38,
    prog: 91,
    tone: "primary"
  }];
  const notifs = [{
    icon: "mail",
    tint: "primary",
    text: "Nuevas calificaciones importadas en Algoritmos Avanzados",
    time: "hace 2 horas"
  }, {
    icon: "warning",
    tint: "error",
    text: "14 alumnos por debajo del umbral en Sistemas Distribuidos",
    time: "ayer, 16:15"
  }, {
    icon: "check_circle",
    tint: "tertiary",
    text: "Comunicación enviada a 9 alumnos atrasados",
    time: "20 sep 2024"
  }];
  const tintBg = {
    primary: "color-mix(in srgb, var(--primary) 18%, transparent)",
    error: "var(--error-container)",
    tertiary: "var(--tertiary-container)"
  };
  const tintFg = {
    primary: "var(--primary)",
    error: "var(--error)",
    tertiary: "var(--tertiary)"
  };
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "flex-end",
      marginBottom: 24,
      gap: 16,
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      fontSize: 32,
      fontWeight: 700,
      letterSpacing: "-0.01em",
      color: "var(--on-surface)"
    }
  }, "Hola, Elena"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "4px 0 0",
      fontSize: 15,
      color: "var(--on-surface-variant)"
    }
  }, "Ten\xE9s 14 alumnos en riesgo y 3 importaciones pendientes hoy.")), /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: "right"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: "var(--outline)"
    }
  }, "Cuatrimestre"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 14,
      fontWeight: 700,
      color: "var(--on-surface)"
    }
  }, "2\xB0 Cuatrimestre 2024"))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(4, 1fr)",
      gap: 24,
      marginBottom: 24
    }
  }, /*#__PURE__*/React.createElement(StatCard, {
    tone: "primary",
    label: "Materias activas",
    value: "06",
    icon: "menu_book",
    trend: "2 con entregas pendientes"
  }), /*#__PURE__*/React.createElement(StatCard, {
    label: "Alumnos totales",
    value: "142",
    icon: "group",
    progress: 88,
    trend: "+8 este cuatrimestre"
  }), /*#__PURE__*/React.createElement(StatCard, {
    label: "En riesgo",
    value: "14",
    icon: "warning",
    trendDir: "down",
    trend: "\u22123 esta semana",
    progress: 32
  }), /*#__PURE__*/React.createElement(StatCard, {
    label: "Promedio general",
    value: "7.4",
    icon: "trending_up",
    trend: "+0.3 vs. parcial",
    progress: 74
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1.4fr 1fr",
      gap: 24
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Cursos activos",
    icon: "menu_book",
    action: /*#__PURE__*/React.createElement(Button, {
      variant: "ghost",
      size: "sm",
      trailingIcon: "arrow_forward",
      onClick: onOpenMaterias
    }, "Ver todas")
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 12
    }
  }, cursos.map(c => /*#__PURE__*/React.createElement("div", {
    key: c.code,
    onClick: onOpenMaterias,
    style: {
      display: "flex",
      alignItems: "center",
      gap: 16,
      padding: 12,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)",
      cursor: "pointer"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 44,
      height: 44,
      borderRadius: "var(--radius-md)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: `color-mix(in srgb, var(--${c.tone}) 18%, transparent)`,
      color: `var(--${c.tone})`
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined"
  }, "terminal")), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 14,
      fontWeight: 700,
      color: "var(--on-surface)"
    }
  }, c.name), /*#__PURE__*/React.createElement(Badge, {
    tone: "neutral"
  }, c.code)), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: "var(--on-surface-variant)",
      marginTop: 2
    }
  }, c.comision, " \xB7 ", c.alumnos, " alumnos")), /*#__PURE__*/React.createElement("div", {
    style: {
      width: 120
    }
  }, /*#__PURE__*/React.createElement(ProgressBar, {
    value: c.prog,
    showValue: true,
    tone: c.tone === "tertiary" ? "success" : "primary"
  })))))), /*#__PURE__*/React.createElement(Card, {
    title: "Notificaciones",
    icon: "notifications",
    action: /*#__PURE__*/React.createElement(Badge, {
      tone: "primary"
    }, "3 nuevas")
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, notifs.map((n, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: "flex",
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 32,
      height: 32,
      flexShrink: 0,
      borderRadius: "var(--radius-full)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: tintBg[n.tint],
      color: tintFg[n.tint]
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 18
    }
  }, n.icon)), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 13,
      color: "var(--on-surface)",
      lineHeight: 1.4
    }
  }, n.text), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "2px 0 0",
      fontSize: 11,
      color: "var(--outline)"
    }
  }, n.time))))))));
}
Object.assign(window, {
  DashboardScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/activia-trace/DashboardScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/activia-trace/LoginScreen.jsx
try { (() => {
// LoginScreen — email + password + tenant ID, with optional 2FA step.
const {
  Input,
  Button
} = window.ActiviaTraceDesignSystem_944743;
function LoginScreen({
  onLogin
}) {
  const [step, setStep] = React.useState("credentials"); // credentials | twofa
  const [email, setEmail] = React.useState("elena.vance@uni.edu");
  const [pwd, setPwd] = React.useState("••••••••••");
  const [tenant, setTenant] = React.useState("universidad-central");
  const [code, setCode] = React.useState(["", "", "", "", "", ""]);
  const setDigit = (i, v) => {
    if (!/^\d?$/.test(v)) return;
    const next = [...code];
    next[i] = v;
    setCode(next);
    if (v && i < 5) {
      const el = document.getElementById("otp-" + (i + 1));
      if (el) el.focus();
    }
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      minHeight: "100vh",
      background: "var(--background)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: 24,
      position: "relative",
      overflow: "hidden"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: "absolute",
      top: "-20%",
      right: "-10%",
      width: 600,
      height: 600,
      background: "color-mix(in srgb, var(--primary) 8%, transparent)",
      filter: "blur(140px)",
      borderRadius: "50%",
      pointerEvents: "none"
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "absolute",
      bottom: "-20%",
      left: "-10%",
      width: 600,
      height: 600,
      background: "color-mix(in srgb, var(--tertiary) 5%, transparent)",
      filter: "blur(150px)",
      borderRadius: "50%",
      pointerEvents: "none"
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      width: 400,
      maxWidth: "100%",
      position: "relative",
      zIndex: 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      justifyContent: "center",
      marginBottom: 28
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 44,
      height: 44,
      background: "var(--primary)",
      borderRadius: "var(--radius-md)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      color: "var(--on-primary)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 26,
      fontVariationSettings: "'FILL' 1"
    }
  }, "analytics")), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 22,
      fontWeight: 700,
      letterSpacing: "-0.02em",
      color: "var(--on-surface)"
    }
  }, "Activia-Trace"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 9,
      letterSpacing: "0.18em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)",
      opacity: 0.6
    }
  }, "Academic Management"))), /*#__PURE__*/React.createElement("div", {
    style: {
      background: "var(--surface-container)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-lg)",
      padding: 28
    }
  }, step === "credentials" ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: "0 0 4px",
      fontSize: 22,
      fontWeight: 700,
      letterSpacing: "-0.01em",
      color: "var(--on-surface)"
    }
  }, "Iniciar sesi\xF3n"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "0 0 24px",
      fontSize: 14,
      color: "var(--on-surface-variant)"
    }
  }, "Ingres\xE1 a tu instituci\xF3n para continuar."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(Input, {
    label: "Email",
    icon: "mail",
    type: "email",
    value: email,
    onChange: e => setEmail(e.target.value)
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Contrase\xF1a",
    icon: "lock",
    type: "password",
    value: pwd,
    onChange: e => setPwd(e.target.value)
  }), /*#__PURE__*/React.createElement(Input, {
    label: "ID de Instituci\xF3n (tenant)",
    icon: "domain",
    value: tenant,
    onChange: e => setTenant(e.target.value),
    helper: "Identificador provisto por tu instituci\xF3n"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "flex-end",
      marginTop: -4
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      fontSize: 13,
      color: "var(--primary)",
      textDecoration: "none",
      fontWeight: 500
    }
  }, "\xBFOlvidaste tu contrase\xF1a?")), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    size: "lg",
    fullWidth: true,
    trailingIcon: "arrow_forward",
    onClick: () => setStep("twofa")
  }, "Continuar"))) : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("button", {
    onClick: () => setStep("credentials"),
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 4,
      background: "none",
      border: "none",
      color: "var(--on-surface-variant)",
      fontSize: 13,
      cursor: "pointer",
      padding: 0,
      marginBottom: 16
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 16
    }
  }, "arrow_back"), " Volver"), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: "0 0 4px",
      fontSize: 22,
      fontWeight: 700,
      letterSpacing: "-0.01em",
      color: "var(--on-surface)"
    }
  }, "Verificaci\xF3n 2FA"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "0 0 24px",
      fontSize: 14,
      color: "var(--on-surface-variant)"
    }
  }, "Ingres\xE1 el c\xF3digo de 6 d\xEDgitos de tu app de autenticaci\xF3n."), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 8,
      justifyContent: "space-between",
      marginBottom: 24
    }
  }, code.map((d, i) => /*#__PURE__*/React.createElement("input", {
    key: i,
    id: "otp-" + i,
    value: d,
    onChange: e => setDigit(i, e.target.value),
    maxLength: 1,
    inputMode: "numeric",
    style: {
      width: 48,
      height: 56,
      textAlign: "center",
      fontSize: 22,
      fontWeight: 700,
      background: "var(--surface-container-low)",
      color: "var(--on-surface)",
      border: `1px solid ${d ? "var(--primary)" : "var(--outline-variant)"}`,
      borderRadius: "var(--radius-md)",
      outline: "none",
      fontFamily: "var(--font-mono)"
    }
  }))), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    size: "lg",
    fullWidth: true,
    onClick: onLogin
  }, "Verificar e ingresar"), /*#__PURE__*/React.createElement("p", {
    style: {
      textAlign: "center",
      margin: "16px 0 0",
      fontSize: 13,
      color: "var(--on-surface-variant)"
    }
  }, "\xBFNo recibiste el c\xF3digo? ", /*#__PURE__*/React.createElement("a", {
    href: "#",
    style: {
      color: "var(--primary)",
      textDecoration: "none"
    }
  }, "Reenviar")))), /*#__PURE__*/React.createElement("p", {
    style: {
      textAlign: "center",
      margin: "20px 0 0",
      fontSize: 11,
      letterSpacing: "0.1em",
      textTransform: "uppercase",
      color: "var(--outline)"
    }
  }, "\xA9 2024 Activia-Trace \xB7 Nexo Academic Systems")));
}
Object.assign(window, {
  LoginScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/activia-trace/LoginScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/activia-trace/MateriaTabs.jsx
try { (() => {
// MateriaTabs — the 5 tab panels for a subject (Materia) detail view.
const {
  Card,
  Button,
  Badge,
  Tag,
  Input,
  Select,
  Checkbox,
  ProgressBar,
  StatCard,
  Avatar
} = window.ActiviaTraceDesignSystem_944743;
const ALUMNOS = [{
  name: "Martín Suárez",
  comision: "A",
  comp: 38,
  nota: 4.2,
  rank: 18
}, {
  name: "Lucía Fernández",
  comision: "A",
  comp: 52,
  nota: 5.1,
  rank: 14
}, {
  name: "Diego Romero",
  comision: "B",
  comp: 41,
  nota: 4.8,
  rank: 16
}, {
  name: "Sofía Castro",
  comision: "B",
  comp: 95,
  nota: 9.2,
  rank: 1
}, {
  name: "Tomás Gil",
  comision: "C",
  comp: 88,
  nota: 8.7,
  rank: 3
}, {
  name: "Valentina Ríos",
  comision: "A",
  comp: 29,
  nota: 3.4,
  rank: 22
}];
function SectionTitle({
  children,
  hint
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "baseline",
      gap: 10,
      marginBottom: 14
    }
  }, /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontSize: 14,
      fontWeight: 700,
      letterSpacing: "0.04em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)"
    }
  }, children), hint && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: "var(--outline)"
    }
  }, hint));
}
function Th({
  children,
  align
}) {
  return /*#__PURE__*/React.createElement("th", {
    style: {
      textAlign: align || "left",
      padding: "10px 12px",
      fontSize: 11,
      fontWeight: 600,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: "var(--outline)",
      borderBottom: "1px solid var(--outline-variant)",
      whiteSpace: "nowrap"
    }
  }, children);
}
function Td({
  children,
  align
}) {
  return /*#__PURE__*/React.createElement("td", {
    style: {
      textAlign: align || "left",
      padding: "12px",
      fontSize: 13,
      color: "var(--on-surface)",
      borderBottom: "1px solid var(--outline-variant)"
    }
  }, children);
}

/* ---- 1. Importar Calificaciones ---- */
function ImportarPanel() {
  const [threshold, setThreshold] = React.useState(60);
  const acts = [{
    name: "Parcial 1",
    type: "Examen",
    rows: 142
  }, {
    name: "TP Integrador",
    type: "Trabajo Práctico",
    rows: 138
  }, {
    name: "Quiz Semanal 4",
    type: "Quiz",
    rows: 140
  }];
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 24,
      alignItems: "start"
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Subir archivo",
    icon: "upload_file"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      border: "2px dashed var(--outline-variant)",
      borderRadius: "var(--radius-lg)",
      padding: 40,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      textAlign: "center",
      background: "var(--surface-container-lowest)",
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 56,
      height: 56,
      borderRadius: "var(--radius-full)",
      background: "var(--surface-container-high)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      marginBottom: 14
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 28,
      color: "var(--primary)"
    }
  }, "cloud_upload")), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 14,
      fontWeight: 700,
      color: "var(--on-surface)"
    }
  }, "Arrastr\xE1 tu archivo de notas"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "6px 0 16px",
      fontSize: 12,
      color: "var(--on-surface-variant)"
    }
  }, "Formatos: CSV o XLSX \xB7 M\xE1x 10MB"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    size: "sm",
    icon: "folder_open"
  }, "Seleccionar archivo")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10,
      padding: 12,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      color: "var(--tertiary)"
    }
  }, "description"), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 600
    }
  }, "notas_cs402_2c2024.xlsx"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: "var(--outline)"
    }
  }, "2.4 MB \xB7 142 filas detectadas")), /*#__PURE__*/React.createElement(Badge, {
    tone: "success",
    dot: true
  }, "Listo"))), /*#__PURE__*/React.createElement(Card, {
    title: "Previsualizaci\xF3n",
    icon: "preview",
    action: /*#__PURE__*/React.createElement(Badge, {
      tone: "primary"
    }, acts.length, " actividades")
  }, /*#__PURE__*/React.createElement("table", {
    style: {
      width: "100%",
      borderCollapse: "collapse",
      marginBottom: 20
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement(Th, null, "Actividad"), /*#__PURE__*/React.createElement(Th, null, "Tipo"), /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "Registros"))), /*#__PURE__*/React.createElement("tbody", null, acts.map(a => /*#__PURE__*/React.createElement("tr", {
    key: a.name
  }, /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 600
    }
  }, a.name)), /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement(Tag, null, a.type)), /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, a.rows))))), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 16,
      background: "var(--surface-container-low)",
      borderRadius: "var(--radius-md)",
      border: "1px solid var(--outline-variant)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      fontWeight: 600,
      color: "var(--on-surface)"
    }
  }, "Umbral de aprobaci\xF3n"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 18,
      fontWeight: 800,
      color: "var(--primary)",
      fontFamily: "var(--font-mono)"
    }
  }, threshold, "%")), /*#__PURE__*/React.createElement("input", {
    type: "range",
    min: "0",
    max: "100",
    value: threshold,
    onChange: e => setThreshold(+e.target.value),
    style: {
      width: "100%",
      accentColor: "var(--primary)"
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "flex-end",
      marginTop: 16
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    icon: "check"
  }, "Confirmar importaci\xF3n")))));
}

/* ---- 2. Alumnos Atrasados (4 subvistas) ---- */
function AtrasadosPanel() {
  const [sub, setSub] = React.useState("atrasados");
  const atrasados = ALUMNOS.filter(a => a.comp < 60).sort((a, b) => a.comp - b.comp);
  const ranking = [...ALUMNOS].sort((a, b) => a.rank - b.rank);
  const subs = [{
    id: "atrasados",
    label: "Atrasados",
    icon: "warning"
  }, {
    id: "ranking",
    label: "Ranking",
    icon: "leaderboard"
  }, {
    id: "notas",
    label: "Notas Finales",
    icon: "grading"
  }, {
    id: "reportes",
    label: "Reportes Rápidos",
    icon: "insights"
  }];
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "inline-flex",
      gap: 4,
      padding: 4,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)",
      marginBottom: 20
    }
  }, subs.map(s => /*#__PURE__*/React.createElement("button", {
    key: s.id,
    onClick: () => setSub(s.id),
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 6,
      padding: "7px 12px",
      borderRadius: "var(--radius-sm)",
      border: "none",
      cursor: "pointer",
      fontSize: 13,
      fontWeight: 600,
      background: sub === s.id ? "var(--primary)" : "transparent",
      color: sub === s.id ? "var(--on-primary)" : "var(--on-surface-variant)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 16
    }
  }, s.icon), s.label))), sub === "atrasados" && /*#__PURE__*/React.createElement(Card, {
    padding: 0
  }, /*#__PURE__*/React.createElement("table", {
    style: {
      width: "100%",
      borderCollapse: "collapse"
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement(Th, null, "Alumno"), /*#__PURE__*/React.createElement(Th, null, "Comisi\xF3n"), /*#__PURE__*/React.createElement(Th, null, "Completitud"), /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "Estado"))), /*#__PURE__*/React.createElement("tbody", null, atrasados.map(a => /*#__PURE__*/React.createElement("tr", {
    key: a.name
  }, /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Avatar, {
    name: a.name,
    size: "xs"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 600
    }
  }, a.name))), /*#__PURE__*/React.createElement(Td, null, "Comisi\xF3n ", a.comision), /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 160
    }
  }, /*#__PURE__*/React.createElement(ProgressBar, {
    value: a.comp,
    showValue: true,
    tone: a.comp < 40 ? "primary" : "primary"
  }))), /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "danger",
    dot: true
  }, "En riesgo"))))))), sub === "ranking" && /*#__PURE__*/React.createElement(Card, {
    padding: 0
  }, /*#__PURE__*/React.createElement("table", {
    style: {
      width: "100%",
      borderCollapse: "collapse"
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "#"), /*#__PURE__*/React.createElement(Th, null, "Alumno"), /*#__PURE__*/React.createElement(Th, null, "Comisi\xF3n"), /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "Nota"))), /*#__PURE__*/React.createElement("tbody", null, ranking.map(a => /*#__PURE__*/React.createElement("tr", {
    key: a.name
  }, /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      fontWeight: 700,
      color: a.rank <= 3 ? "var(--primary)" : "var(--on-surface-variant)"
    }
  }, String(a.rank).padStart(2, "0"))), /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Avatar, {
    name: a.name,
    size: "xs"
  }), a.name)), /*#__PURE__*/React.createElement(Td, null, "Comisi\xF3n ", a.comision), /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 700
    }
  }, a.nota.toFixed(1)))))))), sub === "notas" && /*#__PURE__*/React.createElement(Card, {
    padding: 0
  }, /*#__PURE__*/React.createElement("table", {
    style: {
      width: "100%",
      borderCollapse: "collapse"
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement(Th, null, "Alumno"), /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "Nota final"), /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "Resultado"))), /*#__PURE__*/React.createElement("tbody", null, ALUMNOS.map(a => /*#__PURE__*/React.createElement("tr", {
    key: a.name
  }, /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Avatar, {
    name: a.name,
    size: "xs"
  }), a.name)), /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 700,
      fontFamily: "var(--font-mono)"
    }
  }, a.nota.toFixed(1))), /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, a.nota >= 6 ? /*#__PURE__*/React.createElement(Badge, {
    tone: "success",
    dot: true
  }, "Aprobado") : /*#__PURE__*/React.createElement(Badge, {
    tone: "danger",
    dot: true
  }, "Desaprobado"))))))), sub === "reportes" && /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(3, 1fr)",
      gap: 24
    }
  }, /*#__PURE__*/React.createElement(StatCard, {
    label: "Total alumnos",
    value: "142",
    icon: "group"
  }), /*#__PURE__*/React.createElement(StatCard, {
    tone: "primary",
    label: "En riesgo",
    value: "14",
    icon: "warning",
    trend: "9.8% del total"
  }), /*#__PURE__*/React.createElement(StatCard, {
    label: "Promedio general",
    value: "7.4",
    icon: "trending_up",
    progress: 74
  })));
}

/* ---- 3. Comunicar a Atrasados ---- */
function ComunicarPanel() {
  const targets = ALUMNOS.filter(a => a.comp < 60);
  const [sel, setSel] = React.useState(() => new Set(targets.map(t => t.name)));
  const [sent, setSent] = React.useState(false);
  const [statuses, setStatuses] = React.useState({});
  const toggle = name => {
    const n = new Set(sel);
    n.has(name) ? n.delete(name) : n.add(name);
    setSel(n);
  };
  const send = () => {
    setSent(true);
    const chosen = targets.filter(t => sel.has(t.name));
    const init = {};
    chosen.forEach(c => init[c.name] = "pendiente");
    setStatuses(init);
    chosen.forEach((c, i) => {
      setTimeout(() => setStatuses(s => ({
        ...s,
        [c.name]: "enviando"
      })), 400 * (i + 1));
      setTimeout(() => setStatuses(s => ({
        ...s,
        [c.name]: i === 2 ? "fallido" : "ok"
      })), 400 * (i + 1) + 700);
    });
  };
  const statusBadge = st => {
    const map = {
      pendiente: ["neutral", "Pendiente", "schedule"],
      enviando: ["primary", "Enviando", "sync"],
      ok: ["success", "Enviado", "check_circle"],
      fallido: ["danger", "Fallido", "error"],
      cancelado: ["neutral", "Cancelado", "block"]
    };
    const [tone, label, icon] = map[st] || map.pendiente;
    return /*#__PURE__*/React.createElement(Badge, {
      tone: tone,
      icon: icon
    }, label);
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: sent ? "1fr 1fr" : "0.9fr 1.1fr",
      gap: 24,
      alignItems: "start"
    }
  }, /*#__PURE__*/React.createElement(Card, {
    title: "Destinatarios",
    icon: "group",
    action: /*#__PURE__*/React.createElement(Badge, {
      tone: "primary"
    }, sel.size, " seleccionados")
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 8
    }
  }, targets.map(t => /*#__PURE__*/React.createElement("label", {
    key: t.name,
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: 10,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)",
      cursor: "pointer"
    }
  }, /*#__PURE__*/React.createElement(Checkbox, {
    checked: sel.has(t.name),
    onChange: () => toggle(t.name)
  }), /*#__PURE__*/React.createElement(Avatar, {
    name: t.name,
    size: "xs"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 600
    }
  }, t.name), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      color: "var(--outline)"
    }
  }, "Completitud ", t.comp, "%")), sent && statuses[t.name] && statusBadge(statuses[t.name]))))), /*#__PURE__*/React.createElement(Card, {
    title: sent ? "Estado de envíos" : "Previsualización del mensaje",
    icon: sent ? "mark_email_read" : "drafts"
  }, !sent ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: 18,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)",
      marginBottom: 18
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "0 0 12px",
      fontSize: 13,
      fontWeight: 700,
      color: "var(--on-surface)"
    }
  }, "Asunto: Recordatorio de actividades pendientes"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 13,
      lineHeight: 1.6,
      color: "var(--on-surface-variant)"
    }
  }, "Hola ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--primary)"
    }
  }, "{nombre}"), ", notamos que tu completitud en ", /*#__PURE__*/React.createElement("strong", {
    style: {
      color: "var(--on-surface)"
    }
  }, "Algoritmos Avanzados"), " es del ", /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--primary)"
    }
  }, "{completitud}", "%"), ", por debajo del umbral del 60%. Te recomendamos ponerte al d\xEDa con las entregas pendientes antes del cierre del cuatrimestre.")), /*#__PURE__*/React.createElement(Button, {
    variant: "primary",
    icon: "send",
    fullWidth: true,
    onClick: send
  }, "Enviar a ", sel.size, " alumnos")) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 10
    }
  }, targets.filter(t => sel.has(t.name)).map(t => /*#__PURE__*/React.createElement("div", {
    key: t.name,
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: 12,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Avatar, {
    name: t.name,
    size: "xs"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      fontWeight: 600
    }
  }, t.name)), statusBadge(statuses[t.name]))), /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    size: "sm",
    icon: "refresh",
    onClick: () => {
      setSent(false);
      setStatuses({});
    }
  }, "Volver a editar"))));
}

/* ---- 4. Entregas Pendientes ---- */
function EntregasPanel() {
  const rows = [{
    act: "TP Integrador",
    alumno: "Martín Suárez",
    entregado: true,
    corregido: false
  }, {
    act: "Parcial 1",
    alumno: "Valentina Ríos",
    entregado: true,
    corregido: false
  }, {
    act: "Quiz Semanal 4",
    alumno: "Diego Romero",
    entregado: true,
    corregido: true
  }, {
    act: "TP Integrador",
    alumno: "Lucía Fernández",
    entregado: true,
    corregido: false
  }];
  const pendientes = rows.filter(r => !r.corregido);
  return /*#__PURE__*/React.createElement(Card, {
    title: "Entregas sin corregir",
    icon: "assignment_late",
    action: /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      size: "sm",
      icon: "download"
    }, "Exportar CSV")
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 12,
      marginBottom: 18
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      padding: 14,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      textTransform: "uppercase",
      letterSpacing: "0.05em",
      color: "var(--outline)"
    }
  }, "Detectadas sin corregir"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 24,
      fontWeight: 800,
      color: "var(--error)"
    }
  }, pendientes.length)), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      padding: 14,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 11,
      textTransform: "uppercase",
      letterSpacing: "0.05em",
      color: "var(--outline)"
    }
  }, "Total en reporte"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 24,
      fontWeight: 800,
      color: "var(--on-surface)"
    }
  }, rows.length))), /*#__PURE__*/React.createElement("table", {
    style: {
      width: "100%",
      borderCollapse: "collapse"
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement(Th, null, "Actividad"), /*#__PURE__*/React.createElement(Th, null, "Alumno"), /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "Estado"))), /*#__PURE__*/React.createElement("tbody", null, rows.map((r, i) => /*#__PURE__*/React.createElement("tr", {
    key: i
  }, /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 600
    }
  }, r.act)), /*#__PURE__*/React.createElement(Td, null, r.alumno), /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, r.corregido ? /*#__PURE__*/React.createElement(Badge, {
    tone: "success",
    dot: true
  }, "Corregido") : /*#__PURE__*/React.createElement(Badge, {
    tone: "warning",
    dot: true
  }, "Sin corregir")))))));
}

/* ---- 5. Monitor de Seguimiento ---- */
function MonitorPanel() {
  const [q, setQ] = React.useState("");
  const [minComp, setMinComp] = React.useState(0);
  const activities = ["Parcial 1", "TP Integrador", "Quiz 4"];
  const data = ALUMNOS.map(a => ({
    ...a,
    acts: [a.comp > 50, a.comp > 70, a.comp > 30]
  }));
  const filtered = data.filter(a => a.name.toLowerCase().includes(q.toLowerCase()) && a.comp >= minComp);
  return /*#__PURE__*/React.createElement(Card, {
    title: "Monitor de seguimiento",
    icon: "monitoring"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 12,
      marginBottom: 18,
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 220
    }
  }, /*#__PURE__*/React.createElement(Input, {
    icon: "search",
    placeholder: "Buscar por nombre...",
    value: q,
    onChange: e => setQ(e.target.value)
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      width: 160
    }
  }, /*#__PURE__*/React.createElement(Select, {
    placeholder: "Comisi\xF3n",
    options: [{
      value: "A",
      label: "Comisión A"
    }, {
      value: "B",
      label: "Comisión B"
    }, {
      value: "C",
      label: "Comisión C"
    }]
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      width: 160
    }
  }, /*#__PURE__*/React.createElement(Select, {
    placeholder: "Actividad",
    options: activities.map(a => ({
      value: a,
      label: a
    }))
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      padding: "0 12px",
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: "var(--on-surface-variant)",
      whiteSpace: "nowrap"
    }
  }, "Compl. \u2265 ", minComp, "%"), /*#__PURE__*/React.createElement("input", {
    type: "range",
    min: "0",
    max: "100",
    value: minComp,
    onChange: e => setMinComp(+e.target.value),
    style: {
      width: 90,
      accentColor: "var(--primary)"
    }
  }))), /*#__PURE__*/React.createElement("table", {
    style: {
      width: "100%",
      borderCollapse: "collapse"
    }
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement(Th, null, "Alumno"), /*#__PURE__*/React.createElement(Th, null, "Comisi\xF3n"), activities.map(a => /*#__PURE__*/React.createElement(Th, {
    key: a,
    align: "center"
  }, a)), /*#__PURE__*/React.createElement(Th, {
    align: "right"
  }, "Completitud"))), /*#__PURE__*/React.createElement("tbody", null, filtered.map(a => /*#__PURE__*/React.createElement("tr", {
    key: a.name
  }, /*#__PURE__*/React.createElement(Td, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(Avatar, {
    name: a.name,
    size: "xs"
  }), a.name)), /*#__PURE__*/React.createElement(Td, null, "Com. ", a.comision), a.acts.map((done, i) => /*#__PURE__*/React.createElement(Td, {
    key: i,
    align: "center"
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 18,
      color: done ? "var(--tertiary)" : "var(--outline)"
    }
  }, done ? "check_circle" : "radio_button_unchecked"))), /*#__PURE__*/React.createElement(Td, {
    align: "right"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 120,
      marginLeft: "auto"
    }
  }, /*#__PURE__*/React.createElement(ProgressBar, {
    value: a.comp,
    showValue: true
  }))))))));
}
Object.assign(window, {
  ImportarPanel,
  AtrasadosPanel,
  ComunicarPanel,
  EntregasPanel,
  MonitorPanel
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/activia-trace/MateriaTabs.jsx", error: String((e && e.message) || e) }); }

// ui_kits/activia-trace/MateriasScreen.jsx
try { (() => {
// MateriasScreen — list of subjects; selecting one opens the 5-tab detail layout.
const {
  Card,
  Badge,
  Tabs,
  Button,
  ProgressBar
} = window.ActiviaTraceDesignSystem_944743;
const MATERIAS = [{
  code: "CS-402",
  name: "Algoritmos Avanzados",
  comisiones: 2,
  alumnos: 48,
  prog: 78,
  riesgo: 14,
  color: "primary",
  icon: "terminal"
}, {
  code: "DS-301",
  name: "Sistemas Distribuidos",
  comisiones: 1,
  alumnos: 56,
  prog: 42,
  riesgo: 9,
  color: "tertiary",
  icon: "database"
}, {
  code: "MAT-102",
  name: "Lógica y Matemática",
  comisiones: 3,
  alumnos: 38,
  prog: 91,
  riesgo: 2,
  color: "primary",
  icon: "functions"
}, {
  code: "AR-210",
  name: "Arquitectura y Diseño",
  comisiones: 1,
  alumnos: 38,
  prog: 64,
  riesgo: 6,
  color: "primary",
  icon: "memory"
}];
function MateriasScreen({
  selected,
  onSelect,
  onBack
}) {
  const [tab, setTab] = React.useState("importar");
  const materia = MATERIAS.find(m => m.code === selected);
  if (!materia) {
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h1", {
      style: {
        margin: "0 0 4px",
        fontSize: 32,
        fontWeight: 700,
        letterSpacing: "-0.01em",
        color: "var(--on-surface)"
      }
    }, "Mis Materias"), /*#__PURE__*/React.createElement("p", {
      style: {
        margin: "0 0 24px",
        fontSize: 15,
        color: "var(--on-surface-variant)"
      }
    }, "Materias que dict\xE1s este cuatrimestre. Entr\xE1 a una para gestionar calificaciones."), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "grid",
        gridTemplateColumns: "repeat(2, 1fr)",
        gap: 24
      }
    }, MATERIAS.map(m => /*#__PURE__*/React.createElement(Card, {
      key: m.code,
      hover: true,
      style: {
        cursor: "pointer"
      }
    }, /*#__PURE__*/React.createElement("div", {
      onClick: () => onSelect(m.code)
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "flex-start",
        justifyContent: "space-between",
        marginBottom: 16
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 12
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        width: 44,
        height: 44,
        borderRadius: "var(--radius-md)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: `color-mix(in srgb, var(--${m.color}) 18%, transparent)`,
        color: `var(--${m.color})`
      }
    }, /*#__PURE__*/React.createElement("span", {
      className: "material-symbols-outlined"
    }, m.icon)), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 15,
        fontWeight: 700,
        color: "var(--on-surface)"
      }
    }, m.name), /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 12,
        color: "var(--on-surface-variant)",
        marginTop: 2
      }
    }, m.code, " \xB7 ", m.comisiones, " comisi\xF3n", m.comisiones > 1 ? "es" : ""))), m.riesgo > 10 ? /*#__PURE__*/React.createElement(Badge, {
      tone: "danger",
      dot: true
    }, m.riesgo, " en riesgo") : /*#__PURE__*/React.createElement(Badge, {
      tone: "neutral"
    }, m.riesgo, " en riesgo")), /*#__PURE__*/React.createElement("div", {
      style: {
        display: "flex",
        alignItems: "center",
        gap: 16
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        fontSize: 12,
        color: "var(--on-surface-variant)"
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        fontWeight: 700,
        color: "var(--on-surface)"
      }
    }, m.alumnos), " alumnos"), /*#__PURE__*/React.createElement("div", {
      style: {
        flex: 1
      }
    }, /*#__PURE__*/React.createElement(ProgressBar, {
      value: m.prog,
      showValue: true,
      label: "Completitud",
      tone: m.color === "tertiary" ? "success" : "primary"
    }))))))));
  }
  const tabs = [{
    id: "importar",
    label: "Importar Calificaciones",
    icon: "upload_file"
  }, {
    id: "atrasados",
    label: "Alumnos Atrasados",
    icon: "warning",
    badge: materia.riesgo
  }, {
    id: "comunicar",
    label: "Comunicar",
    icon: "send"
  }, {
    id: "entregas",
    label: "Entregas Pendientes",
    icon: "assignment_late"
  }, {
    id: "monitor",
    label: "Monitor de Seguimiento",
    icon: "monitoring"
  }];
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("button", {
    onClick: onBack,
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 4,
      background: "none",
      border: "none",
      color: "var(--on-surface-variant)",
      fontSize: 13,
      cursor: "pointer",
      padding: 0,
      marginBottom: 16
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 16
    }
  }, "arrow_back"), " Mis Materias"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: 20,
      gap: 16,
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 14
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 48,
      height: 48,
      borderRadius: "var(--radius-md)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: `color-mix(in srgb, var(--${materia.color}) 18%, transparent)`,
      color: `var(--${materia.color})`
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 26
    }
  }, materia.icon)), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: 0,
      fontSize: 26,
      fontWeight: 700,
      letterSpacing: "-0.01em",
      color: "var(--on-surface)"
    }
  }, materia.name), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      marginTop: 4
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "neutral"
  }, materia.code), /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: "var(--on-surface-variant)"
    }
  }, materia.alumnos, " alumnos \xB7 ", materia.comisiones, " comisi\xF3n", materia.comisiones > 1 ? "es" : "")))), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    size: "sm",
    icon: "settings"
  }, "Configuraci\xF3n")), /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 24
    }
  }, /*#__PURE__*/React.createElement(Tabs, {
    tabs: tabs,
    value: tab,
    onChange: setTab
  })), tab === "importar" && /*#__PURE__*/React.createElement(window.ImportarPanel, null), tab === "atrasados" && /*#__PURE__*/React.createElement(window.AtrasadosPanel, null), tab === "comunicar" && /*#__PURE__*/React.createElement(window.ComunicarPanel, null), tab === "entregas" && /*#__PURE__*/React.createElement(window.EntregasPanel, null), tab === "monitor" && /*#__PURE__*/React.createElement(window.MonitorPanel, null));
}
Object.assign(window, {
  MateriasScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/activia-trace/MateriasScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/activia-trace/ProfileScreen.jsx
try { (() => {
// ProfileScreen & ErrorScreen.
const {
  Card,
  Avatar,
  Button,
  Badge,
  Input,
  EmptyState
} = window.ActiviaTraceDesignSystem_944743;
function ProfileScreen() {
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: "0 0 24px",
      fontSize: 32,
      fontWeight: 700,
      letterSpacing: "-0.01em",
      color: "var(--on-surface)"
    }
  }, "Mi Perfil"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "320px 1fr",
      gap: 24,
      alignItems: "start"
    }
  }, /*#__PURE__*/React.createElement(Card, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      textAlign: "center",
      gap: 4
    }
  }, /*#__PURE__*/React.createElement(Avatar, {
    name: "Elena Vance",
    size: "lg",
    ring: true
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 18,
      fontWeight: 700,
      color: "var(--on-surface)",
      marginTop: 8
    }
  }, "Dra. Elena Vance"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      color: "var(--on-surface-variant)"
    }
  }, "elena.vance@uni.edu"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 6,
      marginTop: 12,
      flexWrap: "wrap",
      justifyContent: "center"
    }
  }, /*#__PURE__*/React.createElement(Badge, {
    tone: "primary"
  }, "Docente"), /*#__PURE__*/React.createElement(Badge, {
    tone: "neutral"
  }, "Coordinadora"))), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 1,
      background: "var(--outline-variant)",
      margin: "20px 0"
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 12,
      fontSize: 13
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--outline)"
    }
  }, "Instituci\xF3n"), /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--on-surface)",
      fontWeight: 600
    }
  }, "Universidad Central")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--outline)"
    }
  }, "Tenant ID"), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: "var(--font-mono)",
      color: "var(--on-surface-variant)"
    }
  }, "universidad-central")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      justifyContent: "space-between"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      color: "var(--outline)"
    }
  }, "2FA"), /*#__PURE__*/React.createElement(Badge, {
    tone: "success",
    dot: true
  }, "Activo")))), /*#__PURE__*/React.createElement(Card, {
    title: "Informaci\xF3n de la cuenta",
    icon: "badge",
    action: /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      size: "sm",
      icon: "edit"
    }, "Editar")
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(Input, {
    label: "Nombre",
    value: "Elena",
    readOnly: true
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Apellido",
    value: "Vance",
    readOnly: true
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Email",
    icon: "mail",
    value: "elena.vance@uni.edu",
    readOnly: true
  }), /*#__PURE__*/React.createElement(Input, {
    label: "Tel\xE9fono",
    icon: "call",
    value: "+54 11 5555-0142",
    readOnly: true
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 1,
      background: "var(--outline-variant)",
      margin: "24px 0"
    }
  }), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: "0 0 14px",
      fontSize: 13,
      fontWeight: 700,
      letterSpacing: "0.05em",
      textTransform: "uppercase",
      color: "var(--on-surface-variant)"
    }
  }, "Roles asignados"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 10
    }
  }, [["Docente", "Gestión de calificaciones y comunicación", "school"], ["Coordinadora", "Acceso a reportes de toda la carrera", "supervisor_account"]].map(([r, d, ic]) => /*#__PURE__*/React.createElement("div", {
    key: r,
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12,
      padding: 12,
      background: "var(--surface-container-low)",
      border: "1px solid var(--outline-variant)",
      borderRadius: "var(--radius-md)"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      width: 36,
      height: 36,
      borderRadius: "var(--radius-md)",
      background: "color-mix(in srgb, var(--primary) 14%, transparent)",
      color: "var(--primary)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center"
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "material-symbols-outlined",
    style: {
      fontSize: 20
    }
  }, ic)), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      fontWeight: 700,
      color: "var(--on-surface)"
    }
  }, r), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 12,
      color: "var(--on-surface-variant)"
    }
  }, d))))))));
}
function ErrorScreen({
  code,
  onHome
}) {
  const cfg = code === "403" ? {
    title: "Sin permisos",
    message: "No tenés acceso a esta sección. Si creés que es un error, contactá a tu administrador."
  } : {
    title: "Página no encontrada",
    message: "La ruta que buscás no existe o fue movida. Verificá la dirección e intentá de nuevo."
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      minHeight: "60vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center"
    }
  }, /*#__PURE__*/React.createElement(EmptyState, {
    code: code,
    title: cfg.title,
    message: cfg.message,
    action: /*#__PURE__*/React.createElement(Button, {
      variant: "primary",
      icon: "arrow_back",
      onClick: onHome
    }, "Volver al dashboard")
  }));
}
Object.assign(window, {
  ProfileScreen,
  ErrorScreen
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/activia-trace/ProfileScreen.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Avatar = __ds_scope.Avatar;

__ds_ns.Badge = __ds_scope.Badge;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.ProgressBar = __ds_scope.ProgressBar;

__ds_ns.StatCard = __ds_scope.StatCard;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.EmptyState = __ds_scope.EmptyState;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Switch = __ds_scope.Switch;

__ds_ns.Textarea = __ds_scope.Textarea;

__ds_ns.NavItem = __ds_scope.NavItem;

__ds_ns.Tabs = __ds_scope.Tabs;

})();
