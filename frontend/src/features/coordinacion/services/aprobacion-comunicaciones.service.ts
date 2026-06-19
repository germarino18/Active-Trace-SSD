import * as api from '@/shared/services/api';
import type { LotesPendientesResponse } from '../types';

export async function getLotesPendientes(): Promise<LotesPendientesResponse> {
  return api.get<LotesPendientesResponse>('/api/v1/comunicaciones/lotes', { estado: 'pendiente' });
}

export async function aprobarLote(loteId: string): Promise<void> {
  return api.post<void>(`/api/v1/comunicaciones/lotes/${loteId}/aprobar`);
}

export async function cancelarLote(loteId: string): Promise<void> {
  return api.post<void>(`/api/v1/comunicaciones/lotes/${loteId}/cancelar`);
}
