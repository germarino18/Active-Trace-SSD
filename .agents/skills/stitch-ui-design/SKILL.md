---
name: stitch-ui-design
description: Design system "Obsidian — High-Contrast Dark" para activia-trace. Tokens de color, tipografía Geist, componentes UI y 7 pantallas de referencia HTML exportadas desde Stitch MCP. Usar al crear o modificar cualquier componente frontend del proyecto.
---

# Stitch UI Design — Obsidian High-Contrast Dark

> **North Star**: *"Precision in Darkness"* — Developer-grade dark UI. Near-black surfaces, high-contrast text, precise accent colors.

El sistema de diseño completo vive en `stitch-design/DESIGN.md` (definiciones conceptuales) y en las 7 pantallas HTML de `stitch-design/stitch_activia_trace_academic_suite/*/code.html` (implementaciones de referencia).

---

## Tokens de Color

La paleta completa son ~60 tokens Tailwind definidos en cada `code.html`. Los esenciales:

| Token | Hex | Uso |
|-------|-----|-----|
| `primary` | `#a78bfa` | Elementos interactivos, links, focus rings |
| `background` | `#09090b` | True near-black |
| `tertiary` | `#34d399` | Estados success, indicadores positivos |
| `surface` | `#0c0c0f` | Superficie base |
| `surface-container` | `#121215` | Cards, inputs |
| `surface-container-low` | `#0f0f12` | Hover states |
| `surface-container-high` | `#18181b` | Elementos elevados |
| `surface-container-lowest` | `#09090b` | Sidebar, backgrounds extremos |
| `outline` | `#52525b` | Bordes de baja visibilidad |
| `outline-variant` | `#27272a` | Bordes de separación estándar |
| `on-surface` | `#fafafa` | Texto primario (high contrast) |
| `on-surface-variant` | `#a1a1aa` | Texto secundario |
| `error` | `#ef4444` | Solo para errores, nunca decorativo |

**Regla de color**: Escala zinc (`#0c0c0f` → `#27272a`). Violeta para acción, esmeralda para positivo, rojo solo para errores. Sin azules, sin amarillos, sin colores decorativos.

---

## Tipografía

- **Font**: Geist (Google Fonts) — sans-serif moderna, developer-friendly
- **Escala tipográfica** (Tailwind classes):

| Token | Size | Weight | Letter-Spacing | Uso |
|-------|------|--------|----------------|-----|
| `headline-xl` | 48px | 700 | -0.02em | Hero titles |
| `headline-lg` | 32px | 600 | -0.01em | Page titles |
| `body-lg` | 18px | 400 | normal | Lead text |
| `body-md` | 16px | 400 | normal | Body text |
| `label-md` | 14px | 500 | +0.01em | Buttons, labels |
| `label-sm` | 12px | 600 | +0.05em | Captions, metadata |

**Regla**: `#fafafa` para texto primario, `#a1a1aa` para secundario. Siempre alto contraste.

---

## Elevación y Separación

- **Minimal shadows**. Usar bordes para separación: `1px solid #27272a` (outline-variant)
- Active/hover states: cambiar al siguiente tier de surface (`surface` → `surface-container-low`)
- Focus rings: `2px solid #a78bfa` con `2px offset`

---

## Componentes UI

### Botones
| Variante | Classes |
|----------|---------|
| **Primary** | `bg-primary text-on-primary rounded-xl font-label-md` |
| **Secondary** | `border border-outline-variant text-on-surface rounded-xl font-label-md bg-transparent` |
| **Ghost** | `text-on-surface-variant hover:text-primary transition-colors` (solo texto, visible en hover) |

### Cards
```html
<div class="bg-surface-container-lowest rounded-xl border border-outline-variant p-md">
```
- Border radius: `rounded-xl` (0.75rem)
- Background siempre `surface-container-lowest`
- Hover: `translateY(-2px)` + transición 0.3s

### Inputs
```html
<input class="bg-surface-container-low border border-outline-variant rounded-xl py-2 px-4
              text-label-md text-on-surface placeholder:text-outline
              focus:ring-2 focus:ring-primary" />
```
- Fill: `surface-container-low`
- Border: `outline-variant`
- Focus ring: violeta `2px solid #a78bfa`

### Sidebar
```html
<aside class="w-[280px] bg-surface-container-lowest border-r border-outline-variant">
```
- Item activo: `border-r-4 border-primary bg-surface-container-low`
- Item inactivo: `text-on-surface-variant hover:bg-surface-container-low`

### TopNav
```html
<header class="h-16 px-gutter bg-surface-container-lowest border-b border-outline-variant sticky top-0">
```

### Tablas
- Header: `font-label-sm uppercase tracking-wider text-outline`
- Rows: `border-b border-outline-variant hover:bg-surface-container-low`

### Badges / Tags
```html
<span class="px-sm py-1 bg-primary/20 text-primary rounded-full font-label-sm border border-primary/30">
```

### Charts / Barras
- Fill: `bg-surface-container-high` (default), `bg-primary` (active month)
- Hover: `hover:bg-primary-container`

---

## Pantallas de Referencia

Cada pantalla tiene un `code.html` (implementación Tailwind completa) y un `screen.png` (preview visual). Están en `stitch-design/stitch_activia_trace_academic_suite/`:

| Carpeta | Pantalla | Features Relacionadas |
|---------|----------|----------------------|
| `dashboard_principal_dark/` | Academic Dashboard — bento grid con métricas, calendario, notificaciones | C-25 dashboard alumno, C-22 dashboard docente |
| `gesti_n_de_administrador/` | Admin Management — tabla de usuarios con filtros | C-24 frontend-finanzas-y-admin |
| `mi_carrera_y_materias_alumno/` | Student Dashboard — cards de materias, progreso, estado | C-25 frontend-alumno |
| `panel_del_profesor/` | Professor Panel — calificaciones, atrasados, comunicaciones | C-22 frontend-academico-docente |
| `portal_nexo_consultas/` | NEXO Portal — consultas read-only por carrera | C-24 panel NEXO |
| `resultados_y_anal_ticas_dark/` | Results & Analytics — gráficos, distribución de notas | C-27 frontend-analytics |
| `seguimiento_de_ex_menes_dark/` | Exam Tracking — progreso por materia, entregas | C-22 seguimiento, C-25 estado académico |

---

## Layout System

- **Bento Grid**: `display: grid; grid-template-columns: repeat(12, 1fr); gap: 24px`
- **Gutter**: 24px (`p-gutter`)
- **Sidebar width**: 280px fijo
- **Main offset**: `ml-[280px]`
- **Responsive**: `col-span-12 lg:col-span-N` para adaptar columnas

---

## Iconos

- Usar **Material Symbols Outlined** de Google Fonts
- Icon fill weight variable: `font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24`
- Tamaño estándar: `text-[20px]` o `text-[18px]` en contenedores pequeños

---

## Micro-interacciones

```js
// Hover en cards del bento grid
card.addEventListener('mouseenter', () => {
    card.style.transform = 'translateY(-2px)';
    card.style.transition = 'all 0.3s ease';
});
card.addEventListener('mouseleave', () => {
    card.style.transform = 'translateY(0px)';
});

// Botón FAB
<button class="active:scale-95 transition-transform">
```

---

## Reglas del Sistema

1. **Nunca fondos claros**. Mantener consistencia zinc gray.
2. **Bordes sobre sombras** para separación. Interfaz plana y precisa.
3. **Color de acento solo para función**, nunca decoración.
4. **Violeta** (`primary #a78bfa`) = interactivo. **Esmeralda** (`tertiary #34d399`) = positivo. **Rojo** (`error #ef4444`) = solo errores.
5. **Geist** como única fuente. No mezclar tipografías.
6. **High contrast** siempre: `#fafafa` sobre fondos oscuros.

---

## Cuándo cargar esta skill

- Al crear o modificar cualquier componente de UI del frontend (`frontend/src/`)
- Al implementar features de C-22, C-23, C-24, C-25, C-26, C-27
- Al diseñar nuevas pantallas o layouts
- Al revisar consistencia visual del producto

Consultar siempre `stitch-design/DESIGN.md` para la especificación conceptual y los `code.html` correspondientes como guía de implementación.
