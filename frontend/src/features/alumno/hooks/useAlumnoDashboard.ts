import { useQuery } from '@tanstack/react-query';
import type { AlumnoDashboardResponse } from '../types/alumno.types';
import * as alumnoService from '../services/alumno.service';

export function useAlumnoDashboard() {
  return useQuery<AlumnoDashboardResponse>({
    queryKey: ['alumno', 'dashboard'],
    queryFn: () => alumnoService.getDashboard(),
    staleTime: 30_000,
  });
}
