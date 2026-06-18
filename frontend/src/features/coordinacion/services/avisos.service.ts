import * as api from '@/shared/services/api';
import type { Aviso, AvisosResponse } from '../types';

export interface AvisoParams {
  scope?: string;
  vigente?: boolean;
  offset?: number;
  limit?: number;
}

export interface CrearAvisoData {
  titulo: string;
  mensaje: string;
  scope: string;
  scope_value?: string;
  severidad: string;
  vigencia_desde: string;
  vigencia_hasta: string;
  requiere_ack: boolean;
  orden: number;
}

export type ActualizarAvisoData = Partial<CrearAvisoData>;

export async function getAvisos(params?: AvisoParams): Promise<AvisosResponse> {
  return api.get<AvisosResponse>('/api/v1/avisos', params as Record<string, unknown>);
}

export async function getAviso(id: string): Promise<Aviso> {
  return api.get<Aviso>(`/api/v1/avisos/${id}`);
}

export async function crearAviso(data: CrearAvisoData): Promise<Aviso> {
  return api.post<Aviso>('/api/v1/avisos', data);
}

export async function actualizarAviso(id: string, data: ActualizarAvisoData): Promise<Aviso> {
  return api.patch<Aviso>(`/api/v1/avisos/${id}`, data);
}

export async function eliminarAviso(id: string): Promise<void> {
  return api.del<void>(`/api/v1/avisos/${id}`);
}

export async function confirmarAck(avisoId: string): Promise<void> {
  return api.post<void>(`/api/v1/avisos/${avisoId}/ack`);
}
