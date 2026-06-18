import * as api from '@/shared/services/api';
import type { AuditoriaFilters, AuditoriaResponse, RegistroAuditoria } from '../types/auditoria';

export async function getAuditoriaLog(filters: AuditoriaFilters): Promise<AuditoriaResponse> {
  return api.get<AuditoriaResponse>('/api/v1/auditoria/log', filters as Record<string, unknown>);
}

export async function getAuditoriaRegistro(id: string): Promise<RegistroAuditoria> {
  return api.get<RegistroAuditoria>(`/api/v1/auditoria/log/${id}`);
}
