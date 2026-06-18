import * as api from '@/shared/services/api';
import type { MonitorGeneralResponse, MonitorCoordinacionResponse } from '../types';

export interface MonitorGeneralParams {
  dias?: number;
  max_acciones?: number;
  materia_id?: string;
}

export interface MonitorCoordinacionParams {
  desde?: string;
  hasta?: string;
  materia_id?: string;
  usuario_id?: string;
}

export async function getMonitorGeneral(params?: MonitorGeneralParams): Promise<MonitorGeneralResponse> {
  return api.get<MonitorGeneralResponse>('/api/v1/monitor/general', params as Record<string, unknown>);
}

export async function getMonitorCoordinacion(params?: MonitorCoordinacionParams): Promise<MonitorCoordinacionResponse> {
  return api.get<MonitorCoordinacionResponse>('/api/v1/monitor/coordinacion', params as Record<string, unknown>);
}
