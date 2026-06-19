import * as api from '@/shared/services/api';
import type { HiloResumen, Mensaje, ResponderPayload } from '../types/inbox.types';

export async function getHilos(): Promise<HiloResumen[]> {
  return api.get<HiloResumen[]>('/api/v1/inbox/hilos');
}

export async function getHilo(id: string): Promise<Mensaje[]> {
  return api.get<Mensaje[]>(`/api/v1/inbox/hilos/${id}`);
}

export async function responder(id: string, payload: ResponderPayload): Promise<Mensaje> {
  return api.post<Mensaje>(`/api/v1/inbox/hilos/${id}/responder`, payload);
}
