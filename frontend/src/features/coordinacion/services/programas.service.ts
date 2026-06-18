import apiClient, * as api from '@/shared/services/api';
import type { ProgramaMateria, FechaAcademica, ProgramasResponse } from '../types';

export interface FechasParams {
  materia_id?: string;
  cohorte_id?: string;
  tipo?: string;
}

export interface CrearFechaData {
  materia_id: string;
  cohorte_id: string;
  tipo: string;
  instancia: number;
  titulo: string;
  fecha: string;
}

export interface ActualizarFechaData {
  tipo?: string;
  instancia?: number;
  titulo?: string;
  fecha?: string;
}

export async function getProgramas(): Promise<ProgramasResponse> {
  return api.get<ProgramasResponse>('/api/v1/programas');
}

export async function crearPrograma(file: File, data: Record<string, string>): Promise<ProgramaMateria> {
  const formData = new FormData();
  formData.append('file', file);
  for (const [key, value] of Object.entries(data)) {
    formData.append(key, value);
  }
  const response = await apiClient.post<ProgramaMateria>('/api/v1/programas', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function eliminarPrograma(id: string): Promise<void> {
  return api.del<void>(`/api/v1/programas/${id}`);
}

export async function getFechasAcademicas(params?: FechasParams): Promise<FechaAcademica[]> {
  return api.get<FechaAcademica[]>('/api/v1/fechas-academicas', params as Record<string, unknown>);
}

export async function crearFechaAcademica(data: CrearFechaData): Promise<FechaAcademica> {
  return api.post<FechaAcademica>('/api/v1/fechas-academicas', data);
}

export async function actualizarFechaAcademica(id: string, data: ActualizarFechaData): Promise<FechaAcademica> {
  return api.patch<FechaAcademica>(`/api/v1/fechas-academicas/${id}`, data);
}

export async function generarHtmlFechas(materiaId: string, cohorteId: string): Promise<{ html: string }> {
  return api.get<{ html: string }>('/api/v1/fechas-academicas/html', {
    materia_id: materiaId,
    cohorte_id: cohorteId,
  });
}
