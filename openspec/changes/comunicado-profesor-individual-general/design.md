## Context

Governance: **CRÍTICO** — esto es comunicación saliente con aprobación, el dominio más sensible del repo. Por eso este documento fija el contrato del endpoint, la reutilización del pipeline aprobado, RBAC/tenant/auditoría y la semántica de "actividad opcional" de forma explícita, ANTES de escribir código.

Estado actual (grounded):
- `POST /profesor/dictados/{id}/comunicado-atrasados` y `.../comunicado-atrasado-null` (`backend/app/api/v1/routers/profesor.py` ~330–394) exigen `actividad_id: UUID` obligatorio, son **per-dictado**, y derivan el conjunto de alumnos clasificándolos contra el nombre de esa actividad (`prepare_comunicado_atrasados` / `prepare_comunicado_atrasado_null`, `profesor_service.py` ~697–840).
- Ambos terminan llamando a `ComunicacionesService.enqueue_masivo(envio_data, current_user, request)` (`comunicaciones_service.py` ~92). Ese método: valida `materia_id` (NotFound si no existe), carga el tenant, renderiza templates por destinatario con variables `{alumno_nombre, alumno_apellido, materia, docente_nombre}`, crea una `Comunicacion` por destinatario en estado inicial, y **solo** transiciona a `ENVIANDO` si `tenant.aprobacion_comunicaciones` es `False` (auto-aprobado). Si la aprobación está activa, las comunicaciones quedan pendientes para aprobación humana (Pend→Send/Canc). Audita con `AccionAuditoria.COMUNICACION_ENVIAR`.
- `enqueue_masivo` requiere **un** `materia_id` por lote y usa `materia.nombre` como la variable de template `materia` — por construcción, **un lote = una materia**.
- Vista consolidada: `GET /profesor/atrasados` → `AtrasadoGeneral[]` (`{entrada_padron_id, nombre, apellido, dictado_id, materia_nombre, actividades_sin_entrega[]}`). `AtrasadosGeneralPage.tsx` la renderiza como tabla sin botón de comunicado.
- Per-dictado: `AtrasadosDictadoPage.tsx` ya tiene botón "Generar comunicado" con form que exige `actividad_id` (`comunicadoSchema`).

Constraint dura: identidad siempre desde la sesión JWT; repositories filtran por `tenant_id`; el endpoint declara `require_permission`; Pydantic `extra='forbid'`; flujo Routers→Services→Repositories; Strict TDD con DB real (sin mocks de DB).

## Goals / Non-Goals

**Goals:**
- Permitir enviar comunicado a alumnos atrasados con `actividad_id` **opcional** (obviar actividad).
- Soportar **modo individual** (un destinatario) y **modo general / masivo** (todos los desaprobados + atrasados de la vista), incluyendo destinatarios **cross-materia**.
- Reutilizar el pipeline aprobado (`enqueue_masivo` → aprobación) SIN saltearlo.
- Gatear con `Perm.COMUNICACION_ENVIAR`, scope de tenant, auditoría.

**Non-Goals:**
- NO modificar la máquina de estados ni el motor de aprobación de comunicaciones.
- NO cambios de schema/DB ni migración Alembic.
- NO remover los endpoints existentes per-dictado/per-actividad (siguen sirviendo el flujo actual de `AtrasadosDictadoPage`).
- NO traer "materias aprobadas/atrasadas" desde un nuevo campo backend (se derivan en frontend de `GET /profesor/atrasados`).

## Decisions

### D1 — Un endpoint que acepta un conjunto de destinatarios + `actividad_id` opcional (no un endpoint per-alumno dedicado)
Se crea **un** endpoint que recibe una lista explícita de destinatarios. Individual = lista de un elemento; general = lista con todos. El frontend ya posee los datos de cada alumno en `AtrasadoGeneral[]`, así que arma la lista del lado cliente.

Contrato elegido:

```
POST /api/v1/profesor/comunicado-atrasados-flexible
require_permission(Perm.COMUNICACION_ENVIAR)

Request (ComunicadoFlexibleRequest, extra='forbid'):
{
  "actividad_id": "uuid | null",          # OPCIONAL — null = obviar actividad
  "asunto_template": "str (min_length=1)",
  "cuerpo_template": "str (min_length=1)",
  "destinatarios": [                        # min_length=1
    {                                       # ComunicadoDestinatarioItem, extra='forbid'
      "entrada_padron_id": "uuid",
      "dictado_id": "uuid"
    }
  ]
}

Response (reusa ComunicadoResult-shape):
{ "total": int, "lote_id": "uuid | null", "lotes": ["uuid", ...] }
```

- El backend resuelve email/nombre/apellido/materia desde la **entrada de padrón** y el **dictado** server-side (no confía en datos del cliente para email/identidad — solo recibe selectores `entrada_padron_id` + `dictado_id`, ambos validados contra el tenant).
- `actividad_id`, si viene, se valida que pertenezca al tenant y al dictado correspondiente; si es `null`, se omite y el comunicado no se ata a ninguna actividad (queda registrado en auditoría como `actividad_id: null`).

**Alternativa descartada**: endpoint per-alumno `POST /profesor/dictados/{d}/alumnos/{e}/comunicado`. Rechazado: duplica lógica, no resuelve el caso general cross-materia, y obliga a N requests para el modo masivo.

### D2 — Agrupar destinatarios por materia y llamar `enqueue_masivo` una vez por materia
Como `enqueue_masivo` exige un único `materia_id` por lote y usa `materia.nombre` para la variable de template, el servicio agrupa los destinatarios por `materia_id` (vía su `dictado_id` → `dictado.materia_id`) y hace **una llamada a `enqueue_masivo` por materia**. La respuesta agrega `total` (suma) y devuelve la lista de `lote_id` generados; `lote_id` top-level se setea cuando hay un único lote (compat con `ComunicadoResult`).

**Alternativa descartada**: extender `enqueue_masivo` para aceptar `materia_id` por destinatario. Rechazado: toca el motor de comunicaciones (CRÍTICO) y rompe el invariante "un lote = una materia" del que dependen aprobación, worker y la vista de lotes.

### D3 — `materias aprobadas/atrasadas` para el pre-fill se derivan en frontend
El pre-fill del modo individual ("este alumno arrastra estas materias atrasadas/desaprobadas") se construye en el cliente filtrando `AtrasadoGeneral[]` por `entrada_padron_id` (un alumno puede tener varias filas, una por dictado). Evita acoplar el backend con un nuevo campo y mantiene el endpoint enfocado en el envío.

**Alternativa descartada**: nuevo campo backend con el detalle de materias por alumno. Rechazado: `GET /profesor/atrasados` ya trae lo necesario; agregar campo es acoplamiento innecesario.

### D4 — Variables de template cuando se omite la actividad
`enqueue_masivo` solo expone `{alumno_nombre, alumno_apellido, materia, docente_nombre}` — **ninguna depende de la actividad**. Por lo tanto omitir `actividad_id` no rompe el render: las mismas cuatro variables siguen disponibles. No se introducen variables nuevas de actividad en este change.

### D5 — Reutilización estricta del gate de aprobación
El nuevo método de servicio NO transiciona estados ni decide aprobación: delega 100% en `enqueue_masivo`, que ya respeta `tenant.aprobacion_comunicaciones`. Esto garantiza que el endpoint flexible NO puede saltear aprobación. La auditoría adicional del servicio (un log agregando el envío flexible) se suma a la que ya emite `enqueue_masivo` por lote.

### D6 — Frontend: un solo formulario para ambos modos
`AtrasadosGeneralPage` mantiene un único form con `actividad_id` opcional. El estado distingue `modo: 'individual' | 'general'` y, en individual, fija el `destinatario` seleccionado. El schema Zod hace `actividad_id` opcional (`z.string().optional()`).

## Risks / Trade-offs

- [Multi-lote en modo general genera N lotes (uno por materia), no uno solo] → La respuesta devuelve `lotes[]` y `total` agregado; la UI muestra el total y, si hay varios lotes, lo indica. Aprobación sigue siendo por-lote (consistente con el modelo actual).
- [El cliente envía la lista de destinatarios y podría incluir alumnos ajenos al profesor] → El servicio valida cada `entrada_padron_id`/`dictado_id` contra el tenant y contra los dictados vigentes del profesor; descarta los no autorizados o sin email (igual que hoy `prepare_comunicado_*` ignora entradas sin email).
- [Saltear aprobación por error en el nuevo camino] → Mitigado por D5: el servicio nunca llama a `update_estado`; todo va por `enqueue_masivo`. Test de integración verifica que con `aprobacion_comunicaciones=True` las comunicaciones quedan pendientes.
- [Duplicar lógica de resolución de email/identidad] → Se extrae un helper interno reutilizable en `profesor_service.py`; los endpoints viejos pueden migrar luego (fuera de alcance).

## Migration Plan

- Sin migración de datos ni de schema. Despliegue aditivo: nuevo endpoint + nuevos campos frontend. Los endpoints existentes quedan intactos.
- Rollback: revertir el commit; no hay estado persistido nuevo. Las comunicaciones ya encoladas siguen su ciclo normal por el worker/aprobación existentes.

## Open Questions

- ¿La respuesta debe exponer `lotes[]` además de `lote_id`, o conviene un único "lote lógico" que agrupe sub-lotes por materia? Decisión por defecto: exponer `lotes[]` y mantener `lote_id` (primero, o null si hay varios) por compat con `ComunicadoResult`. A confirmar con quien consuma la vista de aprobación.
- ¿El modo general debe excluir alumnos sin email silenciosamente (como hoy) o reportarlos? Default: excluir silenciosamente y reflejarlo en `total` (idéntico al comportamiento actual de `prepare_comunicado_atrasados`).
