import * as api from '@/shared/services/api';
import type { EntregasResponse } from '@/features/academico/types';

export async function getEntregasSinCorregir(): Promise<EntregasResponse> {
  return api.get<EntregasResponse>('/api/v1/entregas/sin-corregir');
}
