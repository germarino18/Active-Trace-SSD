## Context

El frontend existe como React 18 + TypeScript + Vite + TanStack Query + Tailwind CSS. Los tokens del design system Obsidian ya están cargados vía la config de Tailwind (`text-on-surface`, `bg-surface-container-lowest`, etc.), pero no existe una capa de componentes compartidos: cada página reimplementa botones, badges, cards y estados de carga con clases ad-hoc.

La skill `activia-trace-design` provee:
- `styles.css` — tokens CSS completos + Geist/Geist Mono fonts
- `components/<group>/` — React primitives con `.d.ts` y `.prompt.md` por componente
- `_ds_bundle.js` — bundle para contextos no-React (mocks HTML, prototipos)
- `ui_kits/activia-trace/` — pantallas completas de referencia

Hay ~40 páginas stub que muestran texto placeholder al usuario final. Las páginas implementadas usan Tailwind directamente, sin componentes compartidos.

## Goals / Non-Goals

**Goals:**
- Adoptar los React primitives de `activia-trace-design` como capa de componentes canónica
- Implementar todas las páginas stub con UI real + integración al backend existente
- Unificar estados de carga, vacío y error en todos los dominios
- Que cada página sea autocontenida: no depende de estilos ni lógica de otra página

**Non-Goals:**
- No se crean nuevos endpoints backend
- No se modifica el sistema de routing (`App.tsx`)
- No se cambian reglas de negocio ni permisos RBAC
- No se agrega funcionalidad que no exista ya en el backend
- El bundle `_ds_bundle.js` NO se usa en producción React — solo para mocks/HTML

## Decisions

### D1 — Adopción de componentes por copia, no por import de bundle

**Decisión**: Los React primitives de `activia-trace-design` se leen desde `components/<group>/` (la skill los tiene como archivos individuales con `.d.ts`). Se crean wrappers/re-exports en `src/shared/components/ds/` para que el resto de la app los importe desde un barrel canónico.

**Alternativa descartada**: Importar el `_ds_bundle.js` en el bundle de Vite. El bundle usa `window.ActiviaTraceDesignSystem_*` (namespace runtime), incompatible con el tree-shaking de Vite y sin tipos nativos para React.

**Rationale**: Los primitives individuales son tree-shakeable, tipados, y permiten personalización por componente sin romper el DS.

---

### D2 — `styles.css` del DS se importa en el entry point

**Decisión**: `styles.css` de `activia-trace-design` se importa en `src/main.tsx` reemplazando (o complementando) el `index.css` actual. Así los tokens CSS y las fonts Geist están disponibles globalmente.

**Alternativa descartada**: Duplicar los tokens en `tailwind.config.ts`. Ya existen parcialmente — la unificación es más limpia con el import del CSS canónico.

---

### D3 — Un change por dominio dentro de este overhaul

**Decisión**: La implementación se ejecuta dominio por dominio (auth → shell → alumno → academico → tutor → admin → coordinacion → finanzas). Cada dominio es independiente: puede asignarse a un agente distinto y sus tests no solapan con otros dominios.

**Rationale**: Minimiza conflictos de merge, permite progreso incremental visible, y alinea con la estructura de `features/` ya existente.

---

### D4 — Integración al backend: solo endpoints ya implementados

**Decisión**: Los stubs se conectan exclusivamente a endpoints que ya existen en el backend. Si un endpoint no existe, la página muestra `EmptyState` con un mensaje informativo en lugar de un stub genérico.

**Rationale**: Opción B (redesign + integración) no incluye implementar backend nuevo. Los gaps se documentan en el spec del dominio correspondiente.

---

### D5 — Tests: actualizar mocks de render, no reescribir lógica

**Decisión**: Los tests existentes en `frontend/src/test/` se actualizan para reflejar los nuevos selectores (e.g., queries por `role` en lugar de clase CSS). La lógica de mock de TanStack Query y las aserciones de comportamiento se mantienen.

**Rationale**: Los tests verifican comportamiento, no markup. Cambiar el markup no invalida los tests — solo requiere actualizar los selectores.

## Risks / Trade-offs

- **Tests rotos durante migración** → Mitigación: cada dominio se entrega con sus tests actualizados; no se considera "done" hasta que el suite completo pasa.
- **Inconsistencia transitoria** → Durante la migración, dominios no migrados coexisten con dominios migrados. Aceptable porque el layout shell no cambia y las transiciones son por ruta.
- **Componentes del DS que no cubren todos los casos** → Si un primitivo del DS no existe para un caso de uso, se implementa como componente local en `features/<domain>/components/` y se documenta para revisión futura del DS.
- **`styles.css` puede solapar con `tailwind.config.ts`** → El token de color `--primary` ya existe en Tailwind. Si hay conflicto, el CSS custom property del DS tiene precedencia (más específico). Verificar al integrar el entry point.
