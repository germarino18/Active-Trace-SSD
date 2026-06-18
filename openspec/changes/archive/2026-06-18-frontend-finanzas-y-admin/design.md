## Context

Este es el último change del roadmap frontend. C-21 estableció shell + auth, C-22 implementó el workspace PROFESOR, C-23 implementó el workspace COORDINADOR. Este change implementa los workspaces FINANZAS y ADMIN.

Ambos roles comparten la misma estructura de frontend existente: AuthGuard → AppLayout → sidebar con items por permiso. Cada módulo sigue el patrón feature-based ya establecido.

**Estado actual**: Frontend con estructura `src/features/auth/`, `src/features/academico/`, `src/features/coordinacion/`, `src/shared/`, `src/pages/`. Backend endpoints ya disponibles desde C-06 (estructura académica), C-07 (alumnos/entregas), C-18 (liquidaciones), C-19 (auditoría).

## Goals / Non-Goals

**Goals:**
- Implementar feature module `finanzas/` con liquidaciones, grilla salarial y facturas
- Implementar feature module `admin/` con estructura académica, usuarios, auditoría y métricas
- Agregar rutas protegidas por permiso bajo `AuthGuard`
- Agregar items al sidebar para FINANZAS y ADMIN
- Reutilizar componentes compartidos existentes (tablas, formularios, modales, KPIs)

**Non-Goals:**
- No modificar backend — consume APIs existentes
- No modificar componentes compartidos a menos que haga falta un patrón nuevo
- No implementar E2E (se hace en fase de testing separada)

## Decisions

### D1: Feature modules independientes
`features/finanzas/` y `features/admin/` como módulos separados, cada uno con su propia estructura `{components,hooks,services,types,pages}`. Mismo patrón que `features/coordinacion/`.

**Rationale**: Consistencia con C-23. Separación clara de responsabilidades. Cada módulo tiene sus propios tipos, servicios y hooks sin acoplamiento cruzado.

### D2: Sidebar agrupado por rol
Los items de FINANZAS aparecen en el sidebar solo si el usuario tiene `liquidaciones:*` o `facturas:*`. Los items de ADMIN aparecen solo si tiene `estructura:*`, `usuarios:*` o `auditoria:*`.

**Rationale**: Mismo patrón de permisos que en C-23. El `useAuth` hook ya expone permisos del usuario.

### D3: Grilla salarial como pestañas dentro de finanzas
La grilla salarial se implementa como sub-sección con dos pestañas: "Salario base" y "Plus", usando el mismo patrón de `Tabs` que en coordinación.

**Rationale**: Son dos tablas relacionadas que comparten layout y lógica de vigencia. Mejor como pestañas que como rutas separadas.

### D4: Segmentación de liquidaciones con pestañas
La vista de liquidaciones usa tres pestañas: "General", "NEXO", "Factura". Cada una filtra los datos del mismo endpoint con un parámetro de segmento.

**Rationale**: Misma experiencia que FL-08. Evita duplicar la vista por cada segmento.

### D5: Panel de auditoría con diseño de dashboard
El panel de auditoría usa el mismo patrón de dashboard que KPIs: cards superiores con métricas, tabla de log debajo con paginación y filtros. Los gráficos de métricas se implementan como componentes visuales simples (barras con CSS/Tailwind, sin librería de gráficos externa).

**Rationale**: Consistencia con el resto del frontend. Evita dependencias pesadas de charting para gráficos simples.

## Routes

```
/finanzas/liquidaciones          → FINANZAS, ADMIN  (liquidaciones:ver)
/finanzas/grilla-salarial        → FINANZAS          (liquidaciones:configurar-salarios)
/finanzas/facturas               → FINANZAS          (facturas:ver)

/admin/estructura/carreras       → ADMIN             (estructura:ver)
/admin/estructura/cohortes       → ADMIN             (estructura:ver)
/admin/estructura/materias       → ADMIN             (estructura:ver)
/admin/usuarios                  → ADMIN             (usuarios:ver)
/admin/auditoria                 → ADMIN, COORDINADOR (auditoria:ver)
/admin/auditoria/metricas        → ADMIN, COORDINADOR (auditoria:ver)
```

## Component Tree

```
AppLayout
├── Sidebar (nuevos items)
│   ├── Liquidaciones        [liquidaciones:*]
│   ├── Grilla Salarial      [liquidaciones:configurar-salarios]
│   ├── Facturas             [facturas:*]
│   ├── ─────────
│   ├── Estructura Académica [estructura:*]
│   ├── Usuarios             [usuarios:*]
│   └── Auditoría            [auditoria:*]
│
├── LiquidacionesPage
│   ├── LiquidacionKPIs
│   ├── SegmentTabs (General / NEXO / Factura)
│   ├── LiquidacionTable
│   │   └── DocenteRow (expandible con detalle)
│   ├── CerrarLiquidacionModal
│   └── HistorialSection
│       └── LiquidacionCerradaRow
│
├── GrillaSalarialPage
│   ├── SalaryTabs (SalarioBase / Plus)
│   ├── SalarioBaseTable
│   ├── PlusTable
│   └── SalaryFormModal
│
├── FacturasPage
│   ├── FacturaFilters
│   ├── FacturaTable
│   ├── FacturaFormModal
│   └── FacturaDeleteConfirmModal
│
├── EstructuraAcademicaSection
│   ├── SubNav (Carreras / Cohortes / Materias)
│   ├── CarrerasPage (CRUD)
│   ├── CohortesPage (CRUD)
│   └── MateriasPage (CRUD + programas + evaluaciones)
│
├── UsuariosPage
│   ├── UsuarioFilters
│   ├── UsuarioTable
│   └── UsuarioFormModal
│
├── AuditoriaPage
│   ├── AuditoriaFilters
│   ├── AuditoriaTable
│   └── AuditoriaDetailModal
│
└── MetricasPage
    ├── MetricFilters
    ├── AccionesPorDiaChart
    ├── EstadosComunicacionChart
    └── InteraccionesDocenteTable
```

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| Volumen de páginas CRUD puede generar archivos grandes | Usar Table/FormModal genéricos (ya existen en shared). Cada página CRUD <200 LOC |
| La grilla salarial con vigencia requiere validación de solapamientos | La validación se delega al backend; el frontend muestra errores 422 del API |
| Sin librería de gráficos, los charts pueden quedar básicos | Tailwind + CSS grid alcanzan para barras y tabs. Si se necesita más, se agrega recharts como dependencia opt-in |
| C-24 es el change más grande del roadmap (7 capacidades) | Dividir en tasks atómicas. Cada spec file es un grupo de tasks independiente |

## Open Questions

- (ninguna) — todas las decisiones de dominio están cerradas según KB y CHANGES.md
