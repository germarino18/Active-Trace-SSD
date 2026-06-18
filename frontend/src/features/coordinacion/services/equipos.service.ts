import * as api from '@/shared/services/api';
import apiClient from '@/shared/services/api';
import type { Asignacion, AsignacionesResponse, Docente } from '../types';

export interface EquiposFilters {
  materia?: string;
  carrera?: string;
  cohorte?: string;
  usuario?: string;
  rol?: string;
  page?: number;
  per_page?: number;
}

export interface CrearAsignacionData {
  usuario_id: string;
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  rol: string;
  vigencia_desde: string;
  vigencia_hasta: string;
}

export interface ActualizarAsignacionData {
  rol?: string;
  vigencia_desde?: string;
  vigencia_hasta?: string;
  estado?: string;
}

export interface AsignacionMasivaData {
  usuario_ids: string[];
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  rol: string;
  vigencia_desde: string;
  vigencia_hasta: string;
}

export interface ClonarEquipoData {
  origen_materia_id: string;
  origen_carrera_id: string;
  origen_cohorte_id: string;
  destino_materia_id: string;
  destino_carrera_id: string;
  destino_cohorte_id: string;
}

export interface ModificarVigenciaData {
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  vigencia_hasta: string;
}

export interface AsignacionMasivaResponse {
  creadas: number;
  omitidas: number;
}

export interface ClonarEquipoResponse {
  clonadas: number;
}

export async function getMisEquipos(): Promise<AsignacionesResponse> {
  return api.get<AsignacionesResponse>('/api/v1/equipos/mis-equipos');
}

export async function getEquipos(params?: EquiposFilters): Promise<AsignacionesResponse> {
  return api.get<AsignacionesResponse>('/api/v1/equipos', params as Record<string, unknown>);
}

export async function getDocentes(): Promise<Docente[]> {
  return api.get<Docente[]>('/api/v1/equipos/docentes');
}

export async function crearAsignacion(data: CrearAsignacionData): Promise<Asignacion> {
  return api.post<Asignacion>('/api/v1/asignaciones', data);
}

export async function actualizarAsignacion(id: string, data: ActualizarAsignacionData): Promise<Asignacion> {
  return api.patch<Asignacion>(`/api/v1/asignaciones/${id}`, data);
}

export async function eliminarAsignacion(id: string): Promise<void> {
  return api.del<void>(`/api/v1/asignaciones/${id}`);
}

export async function asignacionMasiva(data: AsignacionMasivaData): Promise<AsignacionMasivaResponse> {
  return api.post<AsignacionMasivaResponse>('/api/v1/equipos/asignacion-masiva', data);
}

export async function clonarEquipo(data: ClonarEquipoData): Promise<ClonarEquipoResponse> {
  return api.post<ClonarEquipoResponse>('/api/v1/equipos/clonar', data);
}

export async function modificarVigencia(data: ModificarVigenciaData): Promise<void> {
  return api.patch<void>('/api/v1/equipos/vigencia', data);
}

export async function exportarEquipo(params?: EquiposFilters): Promise<Blob> {
  const response = await apiClient.get('/api/v1/equipos/export', {
    params,
    responseType: 'blob',
  });
  return response.data;
}
