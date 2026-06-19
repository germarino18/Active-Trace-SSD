import apiClient, * as api from '@/shared/services/api';
import { normalizeListResponse } from './helpers';
import type {
  Carrera,
  Cohorte,
  Materia,
  Evaluacion,
  CarrerasResponse,
  CohortesResponse,
  MateriasResponse,
  EvaluacionesResponse,
  CrearCarreraData,
  ActualizarCarreraData,
  CrearCohorteData,
  ActualizarCohorteData,
  CrearMateriaData,
  ActualizarMateriaData,
  CrearEvaluacionData,
} from '../types/estructura';

// ─── Carreras ──────────────────────────────────────────────────

export async function getCarreras(params?: { activa?: boolean; q?: string }): Promise<CarrerasResponse> {
  const data = await api.get<unknown>('/api/admin/carreras', params as Record<string, unknown>);
  return normalizeListResponse<Carrera>(data);
}

export async function getCarrera(id: string): Promise<Carrera> {
  return api.get<Carrera>(`/api/admin/carreras/${id}`);
}

export async function crearCarrera(data: CrearCarreraData): Promise<Carrera> {
  return api.post<Carrera>('/api/admin/carreras', data);
}

export async function actualizarCarrera(id: string, data: ActualizarCarreraData): Promise<Carrera> {
  return api.put<Carrera>(`/api/admin/carreras/${id}`, data);
}

export async function eliminarCarrera(id: string): Promise<void> {
  return api.del<void>(`/api/admin/carreras/${id}`);
}

export async function toggleCarreraEstado(id: string): Promise<Carrera> {
  return api.patch<Carrera>(`/api/admin/carreras/${id}/estado`);
}

// ─── Cohortes ──────────────────────────────────────────────────

export async function getCohortes(params?: { activa?: boolean; q?: string }): Promise<CohortesResponse> {
  const data = await api.get<unknown>('/api/admin/cohortes', params as Record<string, unknown>);
  return normalizeListResponse<Cohorte>(data);
}

export async function getCohorte(id: string): Promise<Cohorte> {
  return api.get<Cohorte>(`/api/admin/cohortes/${id}`);
}

export async function crearCohorte(data: CrearCohorteData): Promise<Cohorte> {
  return api.post<Cohorte>('/api/admin/cohortes', data);
}

export async function actualizarCohorte(id: string, data: ActualizarCohorteData): Promise<Cohorte> {
  return api.put<Cohorte>(`/api/admin/cohortes/${id}`, data);
}

export async function eliminarCohorte(id: string): Promise<void> {
  return api.del<void>(`/api/admin/cohortes/${id}`);
}

export async function toggleCohorteEstado(id: string): Promise<Cohorte> {
  return api.patch<Cohorte>(`/api/admin/cohortes/${id}/estado`);
}

// ─── Materias ──────────────────────────────────────────────────

export async function getMaterias(params?: { activa?: boolean; q?: string }): Promise<MateriasResponse> {
  const data = await api.get<unknown>('/api/admin/materias', params as Record<string, unknown>);
  return normalizeListResponse<Materia>(data);
}

export async function getMateria(id: string): Promise<Materia> {
  return api.get<Materia>(`/api/admin/materias/${id}`);
}

export async function crearMateria(data: CrearMateriaData): Promise<Materia> {
  return api.post<Materia>('/api/admin/materias', data);
}

export async function actualizarMateria(id: string, data: ActualizarMateriaData): Promise<Materia> {
  return api.put<Materia>(`/api/admin/materias/${id}`, data);
}

export async function toggleMateriaEstado(id: string): Promise<Materia> {
  return api.patch<Materia>(`/api/admin/materias/${id}/estado`);
}

// ─── Programas (file upload) ───────────────────────────────────

export async function subirPrograma(
  materiaId: string,
  file: File,
  titulo: string,
): Promise<{ id: string; archivo_url: string }> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('titulo', titulo);
  const response = await apiClient.post<{ id: string; archivo_url: string }>(
    `/api/admin/materias/${materiaId}/programas`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return response.data;
}

// ─── Evaluaciones ──────────────────────────────────────────────

export async function getEvaluaciones(materiaId?: string): Promise<EvaluacionesResponse> {
  const data = await api.get<unknown>(
    '/api/v1/evaluaciones',
    materiaId ? { materia_id: materiaId } : undefined,
  );
  return normalizeListResponse<Evaluacion>(data);
}

export async function crearEvaluacion(data: CrearEvaluacionData): Promise<Evaluacion> {
  return api.post<Evaluacion>('/api/v1/evaluaciones', data);
}
