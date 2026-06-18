import * as api from '@/shared/services/api';
import type { EncuentrosResponse, InstanciaEncuentro } from '../types';

export interface EncuentrosParams {
  materia_id?: string;
  docente_id?: string;
  estado?: string;
  desde?: string;
  hasta?: string;
  offset?: number;
  limit?: number;
}

export interface CrearSlotData {
  materia_id: string;
  titulo: string;
  dia_semana: number;
  hora_inicio: string;
  hora_fin: string;
  semanas: number;
  url_meet?: string;
}

export interface CrearEncuentroData {
  materia_id: string;
  titulo: string;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  docente_id?: string;
  url_meet?: string;
}

export interface ActualizarInstanciaData {
  estado?: string;
  url_meet?: string;
  url_grabacion?: string;
  comentario_interno?: string;
}

export async function getEncuentros(params?: EncuentrosParams): Promise<EncuentrosResponse> {
  return api.get<EncuentrosResponse>('/api/v1/encuentros', params as Record<string, unknown>);
}

export async function getEncuentro(id: string): Promise<InstanciaEncuentro> {
  return api.get<InstanciaEncuentro>(`/api/v1/encuentros/${id}`);
}

export async function crearSlotRecurrente(data: CrearSlotData): Promise<{ instancias: number }> {
  return api.post<{ instancias: number }>('/api/v1/encuentros/slot', data);
}

export async function crearEncuentroUnico(data: CrearEncuentroData): Promise<InstanciaEncuentro> {
  return api.post<InstanciaEncuentro>('/api/v1/encuentros', data);
}

export async function actualizarInstancia(id: string, data: ActualizarInstanciaData): Promise<InstanciaEncuentro> {
  return api.patch<InstanciaEncuentro>(`/api/v1/encuentros/${id}`, data);
}

export async function generarHtml(id: string): Promise<{ html: string }> {
  return api.get<{ html: string }>(`/api/v1/encuentros/${id}/html`);
}
