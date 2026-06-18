import * as api from '@/shared/services/api';
import type { MonitorResponse } from '../types';

export interface MonitorFilters {
  nombre?: string;
  comision?: string;
  actividad?: string;
  completitud_min?: number;
}

export async function getMonitorData(
  materiaId: string,
  filters?: MonitorFilters,
): Promise<MonitorResponse> {
  return api.get<MonitorResponse>(`/api/v1/materias/${materiaId}/monitor`, {
    ...(filters?.nombre && { nombre: filters.nombre }),
    ...(filters?.comision && { comision: filters.comision }),
    ...(filters?.actividad && { actividad: filters.actividad }),
    ...(filters?.completitud_min != null && { completitud_min: filters.completitud_min }),
  });
}
