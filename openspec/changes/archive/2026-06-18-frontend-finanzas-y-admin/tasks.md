## 1. Setup — Routes, Sidebar y Feature Scaffold

- [x] 1.1 Crear feature modules `features/finanzas/` y `features/admin/` con estructura `{components,hooks,services,types,pages}`
- [x] 1.2 Agregar rutas protegidas para FINANZAS y ADMIN en el router central: `/finanzas/*` y `/admin/*`
- [x] 1.3 Agregar items al sidebar para FINANZAS (Liquidaciones, Grilla Salarial, Facturas) con guards por permiso
- [x] 1.4 Agregar items al sidebar para ADMIN (Estructura Académica, Usuarios, Auditoría) con guards por permiso

## 2. Liquidaciones — Vista del Período

- [x] 2.1 Crear `LiquidacionesPage` con layout de pestañas (General / NEXO / Factura)
- [x] 2.2 Crear `liquidaciones.service.ts` con funciones `getLiquidacion()`, `cerrarLiquidacion()`, `exportarLiquidacion()`, `getHistorial()`
- [x] 2.3 Crear hooks `useLiquidacion`, `useCerrarLiquidacion`, `useHistorial` con TanStack Query
- [x] 2.4 Crear `LiquidacionKPIs` componente con cards de total docentes, monto total, facturas pendientes
- [x] 2.5 Crear `LiquidacionTable` con filas expandibles que muestran detalle por docente (rol, comisiones, salario base, plus, total)
- [x] 2.6 Crear `CerrarLiquidacionModal` con confirmación y manejo de error
- [x] 2.7 Crear `HistorialSection` con listado de liquidaciones cerradas y acceso a detalle en solo lectura
- [x] 2.8 Crear tipos TypeScript para liquidaciones en `features/finanzas/types/liquidaciones.ts`

## 3. Grilla Salarial

- [x] 3.1 Crear `GrillaSalarialPage` con pestañas SalarioBase / Plus
- [x] 3.2 Crear `grilla-salarial.service.ts` con funciones CRUD para salario base y plus
- [x] 3.3 Crear hooks `useSalariosBase`, `usePlus`, `useCrearSalarioBase`, `useEditarSalarioBase`, `useCrearPlus`, `useEditarPlus`
- [x] 3.4 Crear `SalarioBaseTable` con columnas: rol, importe, vigencia desde, vigencia hasta
- [x] 3.5 Crear `PlusTable` con columnas: clave, rol, descripción, importe, vigencia
- [x] 3.6 Crear `SalaryFormModal` reutilizable para crear/editar salario base y plus, con validación de fechas de vigencia
- [x] 3.7 Crear tipos TypeScript para grilla salarial en `features/finanzas/types/grilla-salarial.ts`

## 4. Facturas

- [x] 4.1 Crear `FacturasPage` con tabla paginada y filtros
- [x] 4.2 Crear `facturas.service.ts` con funciones CRUD y cambio de estado
- [x] 4.3 Crear hooks `useFacturas`, `useCrearFactura`, `useEditarFactura`, `useEliminarFactura`, `useCambiarEstadoFactura`
- [x] 4.4 Crear `FacturaFilters` con filtros por docente, estado, rango de fechas y búsqueda libre
- [x] 4.5 Crear `FacturaTable` con columnas: fecha carga, docente, período, detalle, archivo adjunto, tamaño, estado, acciones
- [x] 4.6 Crear `FacturaFormModal` con carga de archivo adjunto
- [x] 4.7 Crear `FacturaDeleteConfirmModal` con confirmación de eliminación
- [x] 4.8 Crear tipos TypeScript para facturas en `features/finanzas/types/facturas.ts`

## 5. Estructura Académica (ADMIN)

- [x] 5.1 Crear layout de sub-navegación con pestañas: Carreras / Cohortes / Materias
- [x] 5.2 Crear `estructura.service.ts` con funciones CRUD para carreras, cohortes y materias
- [x] 5.3 Crear hooks genéricos `useCarreras`, `useCohortes`, `useMaterias` y sus mutaciones CRUD
- [x] 5.4 Crear `CarrerasPage` con tabla, formulario modal y cambio de estado
- [x] 5.5 Crear `CohortesPage` con tabla, formulario modal, fechas de vigencia y cambio de estado
- [x] 5.6 Crear `MateriasPage` con tabla, formulario modal, programas (subida de archivo) y evaluaciones
- [x] 5.7 Crear tipos TypeScript para estructura académica en `features/admin/types/estructura.ts`

## 6. Usuarios del Tenant (ADMIN)

- [x] 6.1 Crear `UsuariosPage` con tabla paginada y filtros por rol/estado/búsqueda
- [x] 6.2 Crear `usuarios.service.ts` con funciones CRUD
- [x] 6.3 Crear hooks `useUsuarios`, `useCrearUsuario`, `useEditarUsuario`
- [x] 6.4 Crear `UsuarioFilters` con select de rol, toggle de estado, campo de búsqueda
- [x] 6.5 Crear `UsuarioTable` con columnas: nombre, email, rol, estado, acciones
- [x] 6.6 Crear `UsuarioFormModal` con campos: nombre, apellido, email, rol, estado, con validación de email duplicado
- [x] 6.7 Crear tipos TypeScript para usuarios en `features/admin/types/usuarios.ts`

## 7. Auditoría (ADMIN)

- [x] 7.1 Crear `AuditoriaPage` con tabla de log paginada y filtros
- [x] 7.2 Crear `auditoria.service.ts` con función `getAuditoriaLog(filters)`
- [x] 7.3 Crear hook `useAuditoriaLog` con TanStack Query y filtros reactivos
- [x] 7.4 Crear `AuditoriaFilters` con rango de fechas, materia, usuario, tipo de acción
- [x] 7.5 Crear `AuditoriaTable` con columnas: fecha, usuario, materia, tipo de acción, IP, agente de usuario
- [x] 7.6 Crear `AuditoriaDetailModal` con detalle completo del registro
- [x] 7.7 Crear tipos TypeScript para auditoría en `features/admin/types/auditoria.ts`

## 8. Métricas del Sistema (ADMIN)

- [x] 8.1 Crear `MetricasPage` con dashboard de KPIs y gráficos
- [x] 8.2 Crear `metricas.service.ts` con funciones para acciones por día, estado de comunicaciones e interacciones
- [x] 8.3 Crear hook `useMetricas` con TanStack Query
- [x] 8.4 Crear `MetricFilters` con rango de fechas, materia, usuario
- [x] 8.5 Crear `AccionesPorDiaChart` (gráfico de barras con Tailwind)
- [x] 8.6 Crear `EstadosComunicacionChart` (distribución de estados con cards de colores)
- [x] 8.7 Crear `InteraccionesDocenteTable` con desglose por tipo de acción
- [x] 8.8 Crear tipos TypeScript para métricas en `features/admin/types/metricas.ts`

## 9. Tests

- [x] 9.1 Escribir tests unitarios para servicios de finanzas (liquidaciones, grilla, facturas)
- [x] 9.2 Escribir tests unitarios para servicios de admin (estructura, usuarios, auditoría, métricas)
- [x] 9.3 Escribir tests de componentes para LiquidacionesPage (KPIs, tabs, modal de cierre)
- [x] 9.4 Escribir tests de componentes para GrillaSalarialPage (tabs, tablas, formulario)
- [x] 9.5 Escribir tests de componentes para FacturasPage (filtros, tabla, CRUD)
- [x] 9.6 Escribir tests de componentes para estructura académica (CarrerasPage, CohortesPage, MateriasPage)
- [x] 9.7 Escribir tests de componentes para UsuariosPage (filtros, tabla, formulario)
- [x] 9.8 Escribir tests de componentes para AuditoriaPage (filtros, tabla, detalle)
- [x] 9.9 Escribir tests de componentes para MetricasPage (filtros, charts, tabla)
