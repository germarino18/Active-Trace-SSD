---
name: activia-trace-design
description: Use this skill to generate well-branded interfaces and assets for Activia-Trace (the "Obsidian" dark academic-management design system), either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `readme.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy
assets out and create static HTML files for the user to view. If working on
production code, you can copy assets and read the rules here to become an expert
in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they
want to build or design, ask some questions, and act as an expert designer who
outputs HTML artifacts _or_ production code, depending on the need.

## Quick reference

**Brand:** Activia-Trace — multi-tenant academic management. Visual language is
**"Obsidian — Precision in Darkness"**: developer-grade, high-contrast dark UI.

**Foundations**
- Dark-only, zinc surfaces: bg `#09090b`, cards `#121215`, hairline border `#27272a`.
- Primary = soft violet `#a78bfa`; accent = emerald `#34d399`; error = `#ef4444`.
- Fonts: **Geist** (UI/display), **Geist Mono** (IDs, timestamps, logs).
- Icons: **Material Symbols Outlined** only. No emoji, no hand-drawn SVG.
- Separation by **hairline borders, not shadows.** Radii 4/8/12/full. 4px grid, 24px gutter.
- Copy is Spanish (voseo), direct second-person; numbers are first-class.

**Using it**
- Link `styles.css` for all tokens + fonts (`--primary`, `--surface-container`, `--font-sans`, …).
- Components live on `window.ActiviaTraceDesignSystem_944743` once `_ds_bundle.js` is loaded
  (run `check_design_system` to confirm the namespace if it changed).
  Available: Button, IconButton, Input, Textarea, Select, Switch, Checkbox,
  Card, StatCard, Badge, Tag, Avatar, ProgressBar, Tabs, NavItem, EmptyState.
- Full screen patterns: `ui_kits/activia-trace/` (login/2FA, dashboard,
  Mis Materias 5-tab layout, Mi Perfil, 403/404).

**Files**
- `readme.md` — full content + visual foundations, iconography, index.
- `tokens/` — colors, typography, spacing, elevation, fonts.
- `components/<group>/` — React primitives (+ `.d.ts`, `.prompt.md`, specimen `.card.html`).
- `guidelines/` — foundation specimen cards.
- `ui_kits/activia-trace/` — interactive product recreation.
