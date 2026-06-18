import { useQuery } from '@tanstack/react-query';
import * as auditoriaService from '../services/auditoria.service';
import type { AuditoriaFilters, AuditoriaResponse } from '../types/auditoria';

export function useAuditoriaLog(filters: AuditoriaFilters) {
  return useQuery<AuditoriaResponse>({
    queryKey: ['auditoria-log', filters],
    queryFn: () => auditoriaService.getAuditoriaLog(filters),
  });
}
