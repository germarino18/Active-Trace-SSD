import * as api from '@/shared/services/api';
import type { Aviso } from '../types';

export interface AvisoParams {
  alcance?: string;
  activo?: boolean;
  skip?: number;
  limit?: number;
}

export interface CrearAvisoData {
  alcance: string;
  materia_id?: string;
  cohorte_id?: string;
  rol_destino?: string;
  severidad: string;
  titulo: string;
  cuerpo: string;
  inicio_en: string;
  fin_en: string;
  orden: number;
  activo?: boolean;
  requiere_ack?: boolean;
}

export type ActualizarAvisoData = Partial<CrearAvisoData>;

export async function getAvisos(params?: AvisoParams): Promise<Aviso[]> {
  return api.get<Aviso[]>('/api/v1/avisos', params as Record<string, unknown>);
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
  return api.post<void>(`/api/v1/avisos/${avisoId}/confirmar`);
}
