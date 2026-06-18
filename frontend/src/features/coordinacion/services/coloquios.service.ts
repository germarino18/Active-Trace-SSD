import * as api from '@/shared/services/api';
import type { ColoquiosResponse, Convocatoria, MetricasColoquio, ReservaColoquio } from '../types';

export interface CrearConvocatoriaData {
  materia_id: string;
  instancia: number;
  dias: {
    fecha: string;
    hora_inicio: string;
    hora_fin: string;
    slots: number;
    cupo_por_slot: number;
  }[];
}

export async function getConvocatorias(): Promise<ColoquiosResponse> {
  return api.get<ColoquiosResponse>('/api/v1/coloquios');
}

export async function getConvocatoria(id: string): Promise<Convocatoria> {
  return api.get<Convocatoria>(`/api/v1/coloquios/${id}`);
}

export async function crearConvocatoria(data: CrearConvocatoriaData): Promise<Convocatoria> {
  return api.post<Convocatoria>('/api/v1/coloquios', data);
}

export async function importarAlumnos(convocatoriaId: string, file: File): Promise<{ alumnos: number }> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<{ alumnos: number }>(
    `/api/v1/coloquios/${convocatoriaId}/importar`,
    formData,
  );
  return response;
}

export async function getMetricas(convocatoriaId: string): Promise<MetricasColoquio> {
  return api.get<MetricasColoquio>(`/api/v1/coloquios/${convocatoriaId}/metricas`);
}

export async function reservarTurno(convocatoriaId: string, diaId: string): Promise<ReservaColoquio> {
  return api.post<ReservaColoquio>(`/api/v1/coloquios/${convocatoriaId}/reservar`, { dia_id: diaId });
}

export async function getResultados(convocatoriaId: string): Promise<ReservaColoquio[]> {
  return api.get<ReservaColoquio[]>(`/api/v1/coloquios/${convocatoriaId}/resultados`);
}
