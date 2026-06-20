import * as api from '@/shared/services/api';
import type {
  ProfesorDashboard,
  DictadoMetricas,
  EntradaPadron,
  AgregarAlumnoData,
  AlumnoDisponible,
  Actividad,
  ActividadCreate,
  CalificacionResponse,
  AtrasadoProfesor,
  AtrasadoGeneral,
  ComunicadoResult,
  ComunicadoAtrasadosData,
  ComunicadoFlexibleData,
  CsvUploadResult,
  MiembroEquipo,
  AvisoProfesor,
  AvisoCreate,
  ColoquioProfesor,
  EditarCalificacionData,
  RegistrarCalificacionData,
  TareaProfesor,
} from '../types';

export async function getProfesorDashboard(): Promise<ProfesorDashboard> {
  return api.get<ProfesorDashboard>('/api/v1/profesor/dashboard');
}

export async function getDictadoMetricas(dictadoId: string): Promise<DictadoMetricas> {
  return api.get<DictadoMetricas>(`/api/v1/profesor/dictados/${dictadoId}/metricas`);
}

export async function getPadronDictado(dictadoId: string): Promise<EntradaPadron[]> {
  // Uses PADRON_GESTIONAR_ALUMNO (which PROFESOR has) — NOT /api/admin/padron (which requires padron:ver)
  return api.get<EntradaPadron[]>(`/api/v1/profesor/dictados/${dictadoId}/padron`);
}

export async function getAlumnosDisponibles(dictadoId: string): Promise<AlumnoDisponible[]> {
  return api.get<AlumnoDisponible[]>(`/api/v1/profesor/dictados/${dictadoId}/alumnos-disponibles`);
}

export async function agregarAlumno(dictadoId: string, data: AgregarAlumnoData): Promise<EntradaPadron> {
  return api.post<EntradaPadron>(`/api/v1/profesor/dictados/${dictadoId}/padron/alumnos`, data);
}

/** Bulk add: POST with {usuario_ids: [...]} */
export async function agregarAlumnosBulk(dictadoId: string, usuario_ids: string[]): Promise<EntradaPadron[]> {
  return api.post<EntradaPadron[]>(`/api/v1/profesor/dictados/${dictadoId}/padron/alumnos`, { usuario_ids });
}

export async function quitarAlumno(dictadoId: string, entradaPadronId: string): Promise<void> {
  return api.del<void>(`/api/v1/profesor/dictados/${dictadoId}/padron/alumnos/${entradaPadronId}`);
}

/** Bulk baja: POST with {entrada_padron_ids: [...]} → 204 */
export async function quitarAlumnosBulk(dictadoId: string, entrada_padron_ids: string[]): Promise<void> {
  return api.post<void>(`/api/v1/profesor/dictados/${dictadoId}/padron/alumnos/bulk-baja`, { entrada_padron_ids });
}

/** @deprecated CSV download moved to per-actividad; kept for backward compat if needed */
export function buildExportCsvUrl(dictadoId: string): string {
  return `/api/v1/profesor/dictados/${dictadoId}/padron/export-csv`;
}

// ---------- Actividades ----------

export async function getActividadesDictado(dictadoId: string): Promise<Actividad[]> {
  return api.get<Actividad[]>(`/api/v1/actividades/dictados/${dictadoId}`);
}

export async function crearActividad(dictadoId: string, data: ActividadCreate): Promise<Actividad> {
  return api.post<Actividad>(`/api/v1/actividades/dictados/${dictadoId}`, data);
}

export async function editarActividad(actividadId: string, data: Partial<ActividadCreate>): Promise<Actividad> {
  return api.patch<Actividad>(`/api/v1/actividades/${actividadId}`, data);
}

export async function eliminarActividad(actividadId: string): Promise<void> {
  return api.del<void>(`/api/v1/actividades/${actividadId}`);
}

// ---------- CSV per-actividad ----------

/** @deprecated Use downloadPlantillaCsv() instead — plain href triggers 401 */
export function buildPlantillaCsvUrl(actividadId: string): string {
  return `/api/v1/actividades/${actividadId}/plantilla-csv`;
}

/**
 * Download the prefilled CSV plantilla via authenticated GET (blob).
 * Cannot be a plain <a href> because the endpoint requires JWT auth.
 */
export async function downloadPlantillaCsv(actividadId: string, filename: string): Promise<void> {
  return api.download(`/api/v1/actividades/${actividadId}/plantilla-csv`, filename);
}

export async function subirCalificacionesCsv(actividadId: string, file: File): Promise<CsvUploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  return api.upload<CsvUploadResult>(`/api/v1/actividades/${actividadId}/calificaciones-csv`, formData);
}

// ---------- Calificaciones individuales ----------

export async function registrarCalificacion(
  actividadId: string,
  data: RegistrarCalificacionData,
): Promise<CalificacionResponse> {
  return api.post<CalificacionResponse>(`/api/v1/actividades/${actividadId}/calificaciones`, data);
}

// ---------- Calificaciones ----------

export async function getCalificacionesDictado(dictadoId: string): Promise<CalificacionResponse[]> {
  // Correct prefix: the calificaciones router is mounted at /api/admin/calificaciones
  // PROFESOR has calificaciones:importar which gates this endpoint
  return api.get<CalificacionResponse[]>(`/api/admin/calificaciones/dictados/${dictadoId}`);
}

export async function editarCalificacion(
  calificacionId: string,
  data: EditarCalificacionData,
): Promise<CalificacionResponse> {
  return api.patch<CalificacionResponse>(`/api/admin/calificaciones/${calificacionId}`, data);
}

// ---------- Atrasados ----------

export async function getAtrasadosProfesor(dictadoId: string): Promise<AtrasadoProfesor[]> {
  return api.get<AtrasadoProfesor[]>(`/api/v1/profesor/dictados/${dictadoId}/atrasados`);
}

/** Cross-materia atrasados: GET /api/v1/profesor/atrasados → plain array */
export async function getAtrasadosGeneralProfesor(): Promise<AtrasadoGeneral[]> {
  return api.get<AtrasadoGeneral[]>('/api/v1/profesor/atrasados');
}

/** Legacy endpoint: comunicado only for atrasado_null subtype */
export interface ComunicadoAtrasadoNullData {
  actividad_id: string;
  asunto_template: string;
  cuerpo_template: string;
}

export async function enviarComunicadoAtrasadoNull(
  dictadoId: string,
  data: ComunicadoAtrasadoNullData,
): Promise<ComunicadoResult> {
  return api.post<ComunicadoResult>(`/api/v1/profesor/dictados/${dictadoId}/comunicado-atrasado-null`, data);
}

/** New unified endpoint: comunicado for either desaprobado or atrasado_null */
export async function enviarComunicadoAtrasados(
  dictadoId: string,
  data: ComunicadoAtrasadosData,
): Promise<ComunicadoResult> {
  return api.post<ComunicadoResult>(`/api/v1/profesor/dictados/${dictadoId}/comunicado-atrasados`, data);
}

/**
 * Flexible comunicado endpoint — POST /api/v1/profesor/comunicado-atrasados-flexible
 *
 * Accepts explicit recipients list + optional actividad_id.
 * Used by both individual (1 destinatario) and general (all atrasados) modes.
 * Always routes through the approval-gated enqueue_masivo pipeline.
 */
export async function enviarComunicadoFlexible(
  data: ComunicadoFlexibleData,
): Promise<ComunicadoResult> {
  return api.post<ComunicadoResult>('/api/v1/profesor/comunicado-atrasados-flexible', data);
}

// ---------- Equipo ----------

export async function getEquipoDictado(dictadoId: string): Promise<MiembroEquipo[]> {
  return api.get<MiembroEquipo[]>(`/api/v1/profesor/dictados/${dictadoId}/equipo`);
}

// ---------- Avisos ----------

export async function getAvisosMios(): Promise<AvisoProfesor[]> {
  // Backend returns a plain array of AvisoVisibleRead — no pagination wrapper
  return api.get<AvisoProfesor[]>('/api/v1/profesor/avisos/mios');
}

export async function crearAvisoProfesor(data: AvisoCreate): Promise<AvisoProfesor> {
  return api.post<AvisoProfesor>('/api/v1/avisos', data);
}

// ---------- Coloquios ----------

export async function getColoquiosMios(): Promise<ColoquioProfesor[]> {
  return api.get<ColoquioProfesor[]>('/api/v1/profesor/coloquios/mios');
}

// ---------- Tareas del profesor ----------

/** GET /api/v1/tareas/mias returns a plain array (NOT {items,total}) */
export async function getMisTareasProfesor(): Promise<TareaProfesor[]> {
  return api.get<TareaProfesor[]>('/api/v1/tareas/mias');
}

export async function cambiarEstadoTareaProfesor(tareaId: string, estado: string): Promise<TareaProfesor> {
  return api.patch<TareaProfesor>(`/api/v1/tareas/${tareaId}/estado`, { estado });
}
