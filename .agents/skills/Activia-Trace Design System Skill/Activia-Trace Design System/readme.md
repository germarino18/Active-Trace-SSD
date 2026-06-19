# Activia-Trace — "Obsidian" Design System

Design system for **Activia-Trace**, a multi-tenant web platform for academic
management. Faculty log in to an institution (tenant), then manage subjects:
import grades, track at-risk students, message them, review submissions, and
monitor per-activity progress.

The visual language is **"Obsidian" — Precision in Darkness**: a developer-grade,
high-contrast dark UI. Near-black zinc surfaces, a soft-violet primary, an
emerald accent, and hairline borders instead of shadows. Clean, fast, functional.

## Sources

This system was reverse-engineered from a Stitch/Tailwind prototype of
Activia-Trace and an accompanying spec. Originals (for whoever has access):

- `uploads/DESIGN.md` — the "Obsidian" north-star spec (colors, type, elevation, rules).
- `uploads/code.html` — Academic dashboard (bento grid, KPI tiles, notifications). **Source of the full Tailwind token config.**
- `uploads/code-5af04c21.html` — Student/career dashboard (progress, subject cards, study materials).
- `uploads/code-ba21aa65.html` — Administrative management (commission scheduling grid, faculty assignment, activity logs).
- `uploads/code-98611e5a.html` — Professor control panel (material upload, exam toggles, submission tracker).
- `uploads/code-0eec91be.html` — Nexo Portal (public knowledge base, FAQs, contact form).
- Product-flow prompt (Spanish): login + 2FA, dashboard, **Mis Materias** with 5 tabs
  (Importar Calificaciones, Alumnos Atrasados, Comunicar, Entregas Pendientes, Monitor),
  Mi Perfil, and 403/404 error screens.

The token names (`surface-container-*`, `on-surface-variant`, `outline-variant`,
etc.) follow a Material-3 role naming convention, applied dark-only.

---

## CONTENT FUNDAMENTALS

**Language.** The product UI ships in **Spanish (Río de la Plata / Argentine
register)** — "Mis Materias", "Alumnos Atrasados", "Comunicar a Atrasados",
"Entregas Pendientes". Voseo is used in instructional copy ("Ingresá tu email",
"Arrastrá tu archivo", "Creés que es un error"). System/diagnostic labels and
the original prototypes lean English (Dashboard, INFO/SUCCESS/WARNING logs);
keep user-facing copy Spanish, technical/log copy may stay English.

**Voice.** Direct, second-person, calm and operational. The app speaks **to**
the user ("Tenés 14 alumnos en riesgo"), not about itself. Short declaratives.
No marketing fluff inside the app; the public Nexo Portal is slightly warmer
("Find answers fast").

**Tone.** Precise and reassuring. State facts and counts; let color carry
urgency rather than exclamation. e.g. "14 alumnos por debajo del umbral", not
"¡Atención! Muchos alumnos en riesgo".

**Casing.** Sentence case for body and buttons ("Confirmar importación").
UPPERCASE with wide tracking (`0.05em`) for small eyebrow labels and section
headers ("PERFORMANCE METRICS", "DESTINATARIOS"). Titles are bold, tight-tracked.

**Numbers & data.** Numerals are first-class — padded ranks ("01", "06"),
percentages with the `%` dimmed, monospace for IDs, timestamps and log lines
("14:22:10 · Subject ID: 49201"). Don't invent decorative stats; every number
should mean something (completitud, umbral, en riesgo, promedio).

**Emoji.** Never. Iconography is Material Symbols only.

**Vibe.** A precision instrument for educators — closer to a trading terminal or
an IDE than a consumer ed-tech app. Dense, scannable, dark, fast.

---

## VISUAL FOUNDATIONS

**Color.** Dark-only, zinc-based. Background is true near-black `#09090b`.
Surfaces step up in *very subtle* increments (`#0f0f12 → #121215 → #18181b →
#1e1e22`) — elevation reads through these tiny shifts plus borders, not shadow.
**Primary** is soft violet `#a78bfa` (links, focus, active, interactive fills);
its container `#7c3aed` backs the one highlighted KPI tile. **Tertiary** is
emerald `#34d399` (success, "Aprobado", "Active", positive trends). **Error**
red `#ef4444` is for failures/risk only. Accent color always carries function —
never decoration. Amber `#fbbf24` appears only as a warning tone in badges.

**Type.** **Geist** for everything (UI, display), **Geist Mono** for IDs,
timestamps, ranks and log lines. Headlines are bold with tight tracking
(`-0.02em` at 48px, `-0.01em` at 32px); body is regular at 16/18px; labels are
medium/semibold 14/12px, the smallest uppercased with `0.05em` tracking. Text is
always high-contrast: `#fafafa` primary, `#a1a1aa` secondary, `#52525b` muted.

**Spacing.** 4px base grid: 4 / 8 / 16 / 24 / 40 / 64. The canonical gap and
page padding is **24px** (the bento `gutter`). Sidebar 256px, header 64px.

**Backgrounds.** Flat near-black. No photographic or illustrated backgrounds.
The only ambient treatment is a **very faint blurred violet/emerald glow**
(radial, ~8–10% opacity, 120–150px blur) behind hero/auth surfaces — subtle,
never loud. No gradients on text or cards (a barely-there `to-transparent` tint
appears inside subject thumbnails only).

**Cards.** `surface-container` fill, **1px `outline-variant` (#27272a) hairline
border**, 12px radius (`lg`), 24px padding, **no shadow** by default. Small
tiles/chips use 8px (`md`) or 4px (`sm`). A "glass" variant (header, floating
menus) uses `rgba(18,18,21,0.8)` + 12px backdrop-blur.

**Borders over shadows.** Separation is done with hairlines. Real shadows are
reserved for genuinely floating elements (FAB, dropdowns) and are soft black
(`0 4px 12px rgba(0,0,0,.45)`). Primary CTAs may carry a faint violet glow.

**Radii.** 4px (chips, tight tiles) · 8px (buttons, inputs, cards-small) · 12px
(panels, bento cards) · full (pills, avatars, search bars, toggles, status dots).

**Hover.** Background lifts **one surface tier** (e.g. `container → container-high`),
text muted→bright, icon muted→violet. Cards may translate up 2px and brighten
their border to `outline`. Links/ghost buttons brighten ~8%.

**Press.** Scale down: buttons `scale(0.97)`, nav/active items `scale(0.98)`.
Quick and springy.

**Focus.** 2px solid violet outline with 2px offset, or a 2px violet ring
(`box-shadow 0 0 0 2px primary/30`) on inputs. Always visible.

**Motion.** Subtle and fast — 120–200ms ease on color/background/transform.
Progress bars animate width in ~1s ease. A few `animate-pulse` status dots for
"live/online". No bounces, no decorative looping motion.

**Transparency & blur.** `color-mix(... N% , transparent)` tints for badge/icon
backgrounds (12–18%) and status dots. Backdrop-blur only on the sticky header
and glass panels.

**Imagery.** Avatars are the main imagery — circular, cool-toned, high-contrast
portraits with subtle violet rim lighting (the prototype used AI headshots).
The system ships an initials-fallback Avatar; supply real images in production.

**Layout rules.** Fixed 256px left sidebar; sticky 64px top header with
breadcrumbs + search + notifications + avatar. Content on a 12-col bento grid,
24px gutters, max width ~1600px. A FAB may float bottom-right.

---

## ICONOGRAPHY

**System: Google Material Symbols — Outlined**, loaded as a variable icon font
(`opsz 20–48, wght 100–700, FILL 0–1`). This is the *only* icon set; it is
declared in `tokens/fonts.css` and used via
`<span class="material-symbols-outlined">dashboard</span>`.

- **Style:** Outlined, weight 400, optical size 24 by default.
- **FILL 1** (solid) is used sparingly for emphasis: the logo glyph, folder
  icons, mail/notification markers, and "active/filled" states.
- **Sizes:** 16–18px inline with labels, 20px nav/header, 24–32px feature tiles.
- **Color:** inherits text color; turns violet on hover/active, emerald/red for
  status. Never multicolor.
- **No emoji, no Unicode dingbats, no hand-rolled SVG icons.** If a glyph is
  missing from Material Symbols, pick the nearest Material name rather than
  drawing one.

Common glyphs in use: `dashboard, menu_book, book, upload_file, warning, send,
monitoring, assignment_late, notifications, person, search, settings,
trending_up, check_circle, folder, mail, verified, filter_list, more_vert,
add, chevron_right, arrow_back, analytics` (logo), `hub`.

**Brand mark.** Wordmark "Activia-Trace" in Geist bold (-0.02em tracking) beside
a violet rounded-square tile holding a filled `analytics` glyph, with a small
uppercase "Academic Management" sub-label. No standalone logo file exists; it is
composed from type + the icon tile (see `guidelines/brand-mark.card.html`).

---

## INDEX

**Root**
- `styles.css` — global entry point (consumers link this). `@import`s only.
- `tokens/` — `fonts.css`, `colors.css`, `typography.css`, `spacing.css`, `elevation.css`.
- `readme.md` — this file. `SKILL.md` — Agent-Skills wrapper.

**Components** (`window.ActiviaTraceDesignSystem_944743.*`)
- `components/forms/` — Button, IconButton, Input, Textarea, Select, Switch, Checkbox
- `components/display/` — Card, StatCard, Badge, Tag, Avatar, ProgressBar
- `components/navigation/` — Tabs, NavItem
- `components/feedback/` — EmptyState
- Each dir has a `*.card.html` specimen (Design System tab → "Components").

**Foundations** (`guidelines/` → Design System tab: Colors / Type / Spacing / Brand)
- Color: primary & accent, neutral surfaces, status & text
- Type: display & headlines, body/labels/mono
- Spacing: scale, radii & borders
- Brand: brand mark, iconography

**UI Kit** (`ui_kits/activia-trace/`)
- `index.html` — interactive app: **login (+2FA) → dashboard → Mis Materias
  (5 tabs) → Mi Perfil → 403/404**. Built from the component primitives.
- Screens: `AppShell`, `LoginScreen`, `DashboardScreen`, `MateriasScreen`,
  `MateriaTabs` (the 5 panels), `ProfileScreen`, `ErrorScreen`, `App`.

**Generated (do not edit):** `_ds_bundle.js`, `_ds_manifest.json`, `_adherence.oxlintrc.json`.
