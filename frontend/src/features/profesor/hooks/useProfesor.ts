import { useMutation, useQuery, useQueryClient, type QueryClient } from '@tanstack/react-query';
import * as profesorService from '../services/profesor.service';
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
import type { ComunicadoAtrasadoNullData } from '../services/profesor.service';

// ---------- Shared invalidation helper (D6) ----------

/**
 * Invalidates all derived caches after any mutation that changes padrón,
 * actividades or calificaciones in a dictado. Call from every mutation's
 * onSuccess to keep stat cards + atrasados views fresh.
 */
export function invalidateDictadoDerived(queryClient: QueryClient, dictadoId: string) {
  queryClient.invalidateQueries({ queryKey: ['profesor', 'metricas', dictadoId] });
  queryClient.invalidateQueries({ queryKey: ['profesor', 'dashboard'] });
  queryClient.invalidateQueries({ queryKey: ['profesor', 'atrasados', dictadoId] });
  queryClient.invalidateQueries({ queryKey: ['profesor', 'atrasados-general'] });
}

// ---------- Dashboard ----------

export function useProfesorDashboard(enabled = true) {
  return useQuery<ProfesorDashboard>({
    queryKey: ['profesor', 'dashboard'],
    queryFn: () => profesorService.getProfesorDashboard(),
    enabled,
  });
}

export function useDictadoMetricas(dictadoId: string) {
  return useQuery<DictadoMetricas>({
    queryKey: ['profesor', 'metricas', dictadoId],
    queryFn: () => profesorService.getDictadoMetricas(dictadoId),
    enabled: !!dictadoId,
  });
}

/**
 * Derives the human display name "Materia — Cohorte" for a dictado.
 * Reads from the metricas cache (already loaded by DictadoDashboardPage).
 * Returns a neutral placeholder while loading — never the raw UUID.
 * Cohorte rendered array-friendly per design D3 (single element today).
 */
export function useDictadoNombre(dictadoId: string): string {
  const { data, isLoading } = useDictadoMetricas(dictadoId);
  if (isLoading || !data) return 'Cargando…';
  const cohortes = data.cohorte_nombre ? [data.cohorte_nombre] : [];
  const cohortePart = cohortes.length > 0 ? ` — ${cohortes.join(', ')}` : '';
  return data.materia_nombre ? `${data.materia_nombre}${cohortePart}` : 'Dictado';
}

export function usePadronDictado(dictadoId: string) {
  return useQuery<EntradaPadron[]>({
    queryKey: ['profesor', 'padron', dictadoId],
    queryFn: () => profesorService.getPadronDictado(dictadoId),
    enabled: !!dictadoId,
  });
}

export function useMutationAgregarAlumno(dictadoId: string) {
  const queryClient = useQueryClient();
  return useMutation<EntradaPadron, Error, AgregarAlumnoData>({
    mutationFn: (data) => profesorService.agregarAlumno(dictadoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'padron', dictadoId] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'alumnos-disponibles', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

/** Bulk add: POST {usuario_ids: [...]} */
export function useMutationAgregarAlumnosBulk(dictadoId: string) {
  const queryClient = useQueryClient();
  return useMutation<EntradaPadron[], Error, string[]>({
    mutationFn: (usuario_ids) => profesorService.agregarAlumnosBulk(dictadoId, usuario_ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'padron', dictadoId] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'alumnos-disponibles', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

export function useMutationQuitarAlumno(dictadoId: string) {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (entradaId) => profesorService.quitarAlumno(dictadoId, entradaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'padron', dictadoId] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'alumnos-disponibles', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

/** Bulk baja: POST {entrada_padron_ids: [...]} → 204 */
export function useMutationQuitarAlumnosBulk(dictadoId: string) {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string[]>({
    mutationFn: (ids) => profesorService.quitarAlumnosBulk(dictadoId, ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'padron', dictadoId] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'alumnos-disponibles', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

// ---------- Actividades ----------

export function useActividadesDictado(dictadoId: string) {
  return useQuery<Actividad[]>({
    queryKey: ['profesor', 'actividades', dictadoId],
    queryFn: () => profesorService.getActividadesDictado(dictadoId),
    enabled: !!dictadoId,
  });
}

export function useMutationCrearActividad(dictadoId: string) {
  const queryClient = useQueryClient();
  return useMutation<Actividad, Error, ActividadCreate>({
    mutationFn: (data) => profesorService.crearActividad(dictadoId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'actividades', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

export function useMutationEliminarActividad(dictadoId: string) {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (actividadId) => profesorService.eliminarActividad(actividadId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'actividades', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

// ---------- CSV per-actividad ----------

export function useMutationSubirCalificacionesCsv() {
  const queryClient = useQueryClient();
  return useMutation<CsvUploadResult, Error, { actividadId: string; file: File; dictadoId: string }>({
    mutationFn: ({ actividadId, file }) => profesorService.subirCalificacionesCsv(actividadId, file),
    onSuccess: (_data, { dictadoId }) => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'calificaciones', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

export function useMutationRegistrarCalificacion(dictadoId: string) {
  const queryClient = useQueryClient();
  return useMutation<CalificacionResponse, Error, { actividadId: string; data: RegistrarCalificacionData }>({
    mutationFn: ({ actividadId, data }) => profesorService.registrarCalificacion(actividadId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'calificaciones', dictadoId] });
      invalidateDictadoDerived(queryClient, dictadoId);
    },
  });
}

// ---------- Calificaciones ----------

export function useCalificacionesDictado(dictadoId: string) {
  return useQuery<CalificacionResponse[]>({
    queryKey: ['profesor', 'calificaciones', dictadoId],
    queryFn: () => profesorService.getCalificacionesDictado(dictadoId),
    enabled: !!dictadoId,
  });
}

export function useMutationEditarCalificacion() {
  const queryClient = useQueryClient();
  return useMutation<CalificacionResponse, Error, { calificacionId: string; data: EditarCalificacionData }>({
    mutationFn: ({ calificacionId, data }) => profesorService.editarCalificacion(calificacionId, data),
    onSuccess: () => {
      // No dictadoId in this hook signature — invalidate broad prefixes (D6)
      queryClient.invalidateQueries({ queryKey: ['profesor', 'calificaciones'] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'metricas'] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'atrasados'] });
      queryClient.invalidateQueries({ queryKey: ['profesor', 'atrasados-general'] });
    },
  });
}

// ---------- Atrasados ----------

export function useAtrasadosProfesor(dictadoId: string) {
  return useQuery<AtrasadoProfesor[]>({
    queryKey: ['profesor', 'atrasados', dictadoId],
    queryFn: () => profesorService.getAtrasadosProfesor(dictadoId),
    enabled: !!dictadoId,
  });
}

export function useMutationComunicadoAtrasadoNull(dictadoId: string) {
  return useMutation<ComunicadoResult, Error, ComunicadoAtrasadoNullData>({
    mutationFn: (data) => profesorService.enviarComunicadoAtrasadoNull(dictadoId, data),
  });
}

export function useMutationComunicadoAtrasados(dictadoId: string) {
  return useMutation<ComunicadoResult, Error, ComunicadoAtrasadosData>({
    mutationFn: (data) => profesorService.enviarComunicadoAtrasados(dictadoId, data),
  });
}

/**
 * Mutation hook for POST /api/v1/profesor/comunicado-atrasados-flexible.
 * Used by AtrasadosGeneralPage for both individual and general sends.
 * On success, invalidates the atrasados-general cache.
 */
export function useMutationComunicadoFlexible() {
  const queryClient = useQueryClient();
  return useMutation<ComunicadoResult, Error, ComunicadoFlexibleData>({
    mutationFn: (data) => profesorService.enviarComunicadoFlexible(data),
    onSuccess: () => {
      // Comunicado does not change padrón data — no need to invalidate atrasados.
      // Optional: refresh so the page stays fresh after a bulk send.
      queryClient.invalidateQueries({ queryKey: ['profesor', 'atrasados-general'] });
    },
  });
}

// ---------- Equipo ----------

export function useEquipoDictado(dictadoId: string) {
  return useQuery<MiembroEquipo[]>({
    queryKey: ['profesor', 'equipo', dictadoId],
    queryFn: () => profesorService.getEquipoDictado(dictadoId),
    enabled: !!dictadoId,
  });
}

// ---------- Avisos ----------

export function useAvisosMios() {
  return useQuery<AvisoProfesor[]>({
    queryKey: ['profesor', 'avisos', 'mios'],
    queryFn: () => profesorService.getAvisosMios(),
  });
}

export function useMutationCrearAviso() {
  const queryClient = useQueryClient();
  return useMutation<AvisoProfesor, Error, AvisoCreate>({
    mutationFn: (data) => profesorService.crearAvisoProfesor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'avisos', 'mios'] });
    },
  });
}

// ---------- Alumnos disponibles ----------

export function useAlumnosDisponibles(dictadoId: string) {
  return useQuery<AlumnoDisponible[]>({
    queryKey: ['profesor', 'alumnos-disponibles', dictadoId],
    queryFn: () => profesorService.getAlumnosDisponibles(dictadoId),
    enabled: !!dictadoId,
  });
}

// ---------- Coloquios ----------

export function useColoquiosMios() {
  return useQuery<ColoquioProfesor[]>({
    queryKey: ['profesor', 'coloquios', 'mios'],
    queryFn: () => profesorService.getColoquiosMios(),
  });
}

// ---------- Cross-materia atrasados ----------

/** Uses GET /api/v1/profesor/atrasados (not per-dictado) → plain array */
export function useAtrasadosGeneralProfesor() {
  return useQuery<AtrasadoGeneral[]>({
    queryKey: ['profesor', 'atrasados-general'],
    queryFn: () => profesorService.getAtrasadosGeneralProfesor(),
  });
}

// ---------- Tareas del profesor ----------

/** GET /api/v1/tareas/mias returns a plain array (NOT {items,total}) */
export function useMisTareasProfesor() {
  return useQuery<TareaProfesor[]>({
    queryKey: ['profesor', 'tareas', 'mias'],
    queryFn: () => profesorService.getMisTareasProfesor(),
  });
}

export function useMutationCambiarEstadoTareaProfesor() {
  const queryClient = useQueryClient();
  return useMutation<TareaProfesor, Error, { tareaId: string; estado: string }>({
    mutationFn: ({ tareaId, estado }) => profesorService.cambiarEstadoTareaProfesor(tareaId, estado),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profesor', 'tareas', 'mias'] });
    },
  });
}
