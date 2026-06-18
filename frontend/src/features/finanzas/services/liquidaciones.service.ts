import * as api from '@/shared/services/api';
import apiClient from '@/shared/services/api';
import type { LiquidacionHistorialItem, LiquidacionKPIs, LiquidacionPeriodo } from '../types/liquidaciones';

export interface LiquidacionFilters {
  periodo: string;
  segmento?: string;
}

export interface CerrarLiquidacionData {
  periodo: string;
}

export async function getLiquidacion(params: LiquidacionFilters): Promise<LiquidacionPeriodo> {
  return api.get<LiquidacionPeriodo>('/api/v1/liquidaciones', params as unknown as Record<string, unknown>);
}

export async function getLiquidacionKPIs(periodo: string): Promise<LiquidacionKPIs> {
  return api.get<LiquidacionKPIs>('/api/v1/liquidaciones/kpis', { periodo });
}

export async function cerrarLiquidacion(data: CerrarLiquidacionData): Promise<LiquidacionPeriodo> {
  return api.post<LiquidacionPeriodo>('/api/v1/liquidaciones/cerrar', data);
}

export async function exportarLiquidacion(periodo: string): Promise<Blob> {
  const response = await apiClient.get('/api/v1/liquidaciones/exportar', {
    params: { periodo },
    responseType: 'blob',
  });
  return response.data;
}

export async function getHistorial(): Promise<LiquidacionHistorialItem[]> {
  return api.get<LiquidacionHistorialItem[]>('/api/v1/liquidaciones/historial');
}
