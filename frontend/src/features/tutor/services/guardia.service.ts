import * as api from '@/shared/services/api';
import type { Guardia, GuardiasResponse, RegistrarGuardiaData } from '../types/tutor.types';

export async function getGuardias(): Promise<GuardiasResponse> {
  return api.get<GuardiasResponse>('/api/v1/encuentros', { tipo: 'guardia' } as Record<string, unknown>);
}

export async function registrarGuardia(data: RegistrarGuardiaData): Promise<Guardia> {
  return api.post<Guardia>('/api/v1/encuentros', data);
}
