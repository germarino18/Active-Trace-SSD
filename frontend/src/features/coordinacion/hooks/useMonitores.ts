import { useQuery } from '@tanstack/react-query';
import * as monitoresService from '../services/monitores.service';
import type { MonitorGeneralResponse, MonitorCoordinacionResponse } from '../types';
import type { MonitorGeneralParams, MonitorCoordinacionParams } from '../services/monitores.service';

export function useMonitorGeneral(filters?: MonitorGeneralParams) {
  return useQuery<MonitorGeneralResponse>({
    queryKey: ['monitor', 'general', filters],
    queryFn: () => monitoresService.getMonitorGeneral(filters),
  });
}

export function useMonitorCoordinacion(filters?: MonitorCoordinacionParams) {
  return useQuery<MonitorCoordinacionResponse>({
    queryKey: ['monitor', 'coordinacion', filters],
    queryFn: () => monitoresService.getMonitorCoordinacion(filters),
  });
}
