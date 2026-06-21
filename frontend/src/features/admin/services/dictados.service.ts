import * as api from '@/shared/services/api';
import { normalizeListResponse } from './helpers';
import type {
  Dictado,
  DictadosResponse,
  CrearDictadoData,
  ActualizarDictadoData,
  DictadoFilters,
} from '../types/dictados';

export async function getDictados(params?: DictadoFilters): Promise<DictadosResponse> {
  const data = await api.get<unknown>('/api/admin/dictados', params as Record<string, unknown>);
  return normalizeListResponse<Dictado>(data);
}

export async function getDictado(id: string): Promise<Dictado> {
  return api.get<Dictado>(`/api/admin/dictados/${id}`);
}

export async function crearDictado(data: CrearDictadoData): Promise<Dictado> {
  return api.post<Dictado>('/api/admin/dictados', data);
}

export async function actualizarDictado(id: string, data: ActualizarDictadoData): Promise<Dictado> {
  return api.put<Dictado>(`/api/admin/dictados/${id}`, data);
}

export async function toggleDictadoEstado(id: string): Promise<Dictado> {
  return api.patch<Dictado>(`/api/admin/dictados/${id}/estado`);
}

export async function eliminarDictado(id: string): Promise<void> {
  return api.del<void>(`/api/admin/dictados/${id}`);
}
