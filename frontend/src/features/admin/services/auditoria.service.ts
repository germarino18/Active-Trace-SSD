import * as api from '@/shared/services/api';
import type { AuditoriaFilters, AuditoriaResponse } from '../types/auditoria';

export async function getAuditoriaLog(filters: AuditoriaFilters): Promise<AuditoriaResponse> {
  return api.get<AuditoriaResponse>('/api/v1/auditoria/log', filters as Record<string, unknown>);
}
