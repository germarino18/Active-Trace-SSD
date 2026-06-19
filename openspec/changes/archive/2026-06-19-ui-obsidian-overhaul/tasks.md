## 1. Fundación del DS (prerequisito de todos)

- [x] 1.1 Importar `styles.css` de `activia-trace-design` en `src/main.tsx` (reemplaza o complementa `index.css`)
- [x] 1.2 Leer `components/` del DS y crear barrel `src/shared/components/ds/index.ts` re-exportando primitives: Button, Card, StatCard, Badge, Tag, Avatar, ProgressBar, Tabs, NavItem, EmptyState, Input, Select, Switch, Checkbox, Textarea
- [x] 1.3 Verificar que los tokens ya en `tailwind.config.ts` no colisionen con los CSS custom properties de `styles.css`; ajustar si hay conflicto
- [x] 1.4 Correr el suite de tests existente (`npm test`) como baseline — documentar conteo inicial

## 2. Auth (Login, 2FA, ForgotPassword, ResetPassword)

- [x] 2.1 Rediseñar `LoginPage.tsx` usando el UI kit `ui_kits/activia-trace/` del DS — mantener lógica de useForm/useAuth intacta
- [x] 2.2 Rediseñar `TwoFactorPage.tsx` con campo OTP 6 dígitos, feedback inline de error y botón cancelar
- [x] 2.3 Rediseñar `ForgotPasswordPage.tsx` con identidad Obsidian
- [x] 2.4 Rediseñar `ResetPasswordPage.tsx` con validación de coincidencia de contraseñas (Zod client-side)
- [x] 2.5 Actualizar tests en `LoginPage.test.tsx` y `TwoFactorPage.test.tsx` para nuevos selectores; verificar suite verde

## 3. Shell (Dashboard, Perfil, Errores)

- [x] 3.1 Implementar `DashboardPage.tsx` con KPIs por rol: detectar rol desde `useAuth()`, mostrar StatCards y sección de actividad reciente con skeleton loaders
- [x] 3.2 Implementar `ProfilePage.tsx` con formulario de edición de perfil y sección de cambio de contraseña usando DS
- [x] 3.3 Rediseñar `ForbiddenPage.tsx` con UI kit 403 del DS — código prominente, descripción en español, botón de retorno
- [x] 3.4 Rediseñar `NotFoundPage.tsx` con UI kit 404 del DS
- [x] 3.5 Actualizar tests de ForgotPasswordPage, ResetPasswordPage; verificar suite verde

## 4. Alumno

- [x] 4.1 Refactorizar `MisMateriasPage.tsx` usando Card y Badge del DS (mantener lógica de TanStack Query)
- [x] 4.2 Implementar `AlumnoDashboardPage.tsx` con StatCards: materias activas, promedio, próximas fechas
- [x] 4.3 Implementar `MateriaDetallePage.tsx` con layout de tabs (Actividades, Calificaciones, Material) usando Tabs del DS
- [x] 4.4 Implementar `AlumnoInboxPage.tsx` con lista de comunicaciones, badge de no leído, y navegación al hilo
- [x] 4.5 Implementar `AlumnoHiloPage.tsx` con visualización de hilo de mensajes
- [x] 4.6 Implementar `ComunicacionDetallePage.tsx` con detalle completo de comunicación
- [x] 4.7 Implementar `MisAvisosPage.tsx`, `MisColoquiosPage.tsx`, `MisFechasPage.tsx`, `MisProgramasPage.tsx` con lista + EmptyState del DS
- [x] 4.8 Implementar `MisComunicacionesPage.tsx` con filtro por estado
- [x] 4.9 Actualizar todos los tests de alumno; verificar suite verde

## 5. Académico (flujo central del profesor)

- [x] 5.1 Implementar `MateriaListPage.tsx` (PROFESOR) con cards de materias navegables usando DS Card
- [x] 5.2 Crear layout de 5 tabs por materia (query param `?tab=`): Importar, Atrasados, Comunicar, Entregas, Monitor
- [x] 5.3 Implementar tab Importar: `ImportarCalificacionesPage.tsx` con drag-and-drop, preview de tabla y confirmación
- [x] 5.4 Implementar tab Atrasados: `VistaAtrasadosPage.tsx` con tabla de alumnos, selección y link a Comunicar
- [x] 5.5 Implementar tab Comunicar: `ComunicacionAtrasadosPage.tsx` con destinatarios editables, redactor y modal preview
- [x] 5.6 Implementar tab Entregas: `EntregasSinCorregirPage.tsx` con lista ordenada por fecha
- [x] 5.7 Implementar tab Monitor: `MonitorSeguimientoPage.tsx` con StatCards de KPIs del grupo
- [x] 5.8 Actualizar tests de académico; verificar suite verde

## 6. Tutor

- [x] 6.1 Implementar `TutorAlumnosPage.tsx` con lista de alumnos, badge "En riesgo" del DS
- [x] 6.2 Implementar `GuardiasListPage.tsx` con lista de guardias, diferenciando próximas de pasadas
- [x] 6.3 Implementar `TutorEntregasSinCorregirPage.tsx` con lista de entregas pendientes scoped al tutor
- [x] 6.4 Actualizar tests de tutor; verificar suite verde

## 7. Admin

- [x] 7.1 Implementar `UsuariosPage.tsx` siguiendo patrón `dashboard-crud-page`: tabla + modal crear/editar + confirm desactivar
- [x] 7.2 Implementar `CarrerasPage.tsx` con CRUD estándar DS
- [x] 7.3 Implementar `CohortesPage.tsx` con CRUD estándar DS
- [x] 7.4 Implementar `MateriasPage.tsx` con CRUD estándar DS
- [x] 7.5 Implementar `EstructuraAcademicaPage.tsx` con vista de árbol Carrera → Cohorte → Materia (acordeón)
- [x] 7.6 Implementar `AuditoriaPage.tsx` con tabla de log, filtros de fecha/tipo, y tipografía monospace para timestamps
- [x] 7.7 Implementar `MetricasPage.tsx` con StatCards de KPIs globales del tenant
- [x] 7.8 Actualizar tests de admin; verificar suite verde

## 8. Coordinación

- [x] 8.1 Implementar `EquiposListPage.tsx` y `EquipoDetallePage.tsx` con DS
- [x] 8.2 Implementar `ClonarEquipoPage.tsx` con formulario de selección de período
- [x] 8.3 Implementar `AsignacionIndividualPage.tsx` y `AsignacionMasivaPage.tsx`
- [x] 8.4 Implementar `EncuentrosListPage.tsx`, `EncuentroCrearPage.tsx`, `EncuentroDetallePage.tsx`
- [x] 8.5 Implementar `ConvocatoriasListPage.tsx`, `ConvocatoriaCrearPage.tsx`, `ConvocatoriaDetallePage.tsx`
- [x] 8.6 Implementar `TareasListPage.tsx`, `TareaCrearPage.tsx`, `TareaDetallePage.tsx`, `MisTareasPage.tsx`
- [x] 8.7 Implementar `ProgramasListPage.tsx`, `ProgramaCrearPage.tsx`
- [x] 8.8 Implementar `AvisosListPage.tsx`, `AvisoCrearPage.tsx`, `AvisoEditarPage.tsx`
- [x] 8.9 Implementar `FechasAcademicasPage.tsx`, `ModificarVigenciaPage.tsx`
- [x] 8.10 Implementar `MonitorCoordinacionPage.tsx`, `MonitorGeneralPage.tsx` con StatCards y métricas
- [x] 8.11 Implementar `MisEquiposPage.tsx`
- [x] 8.12 Actualizar todos los tests de coordinación; verificar suite verde

## 9. Finanzas

- [x] 9.1 Implementar `LiquidacionesPage.tsx` con lista por período, estado y acciones de aprobar/rechazar (rol FINANZAS)
- [x] 9.2 Implementar `GrillaSalarialPage.tsx` con tabla editable para FINANZAS, read-only para otros
- [x] 9.3 Implementar `FacturasPage.tsx` con filtros por período y estado, badge visual de pendientes
- [x] 9.4 Actualizar tests de finanzas; verificar suite verde

## 10. Cierre y validación

- [x] 10.1 Correr suite completo de tests frontend; verificar que todos pasan
- [x] 10.2 Verificar que no quedan páginas con contenido placeholder ("se integrará en próximas actualizaciones", etc.)
- [x] 10.3 Verificar consistencia visual entre dominios: mismos tokens, mismos componentes DS para patrones equivalentes
