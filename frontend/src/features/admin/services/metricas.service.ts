import * as api from '@/shared/services/api';
import type { MetricasResponse, AccionesPorDia, EstadoComunicacion, InteraccionDocente } from '../types/metricas';

export interface AccionesPorDiaFilters {
  fecha_desde?: string;
  fecha_hasta?: string;
}

export interface EstadosComunicacionFilters {
  materia_id?: string;
}

export interface InteraccionesFilters {
  materia_id?: string;
  usuario_id?: string;
}

export async function getMetricasDashboard(): Promise<MetricasResponse> {
  return api.get<MetricasResponse>('/api/admin/metricas');
}

export async function getAccionesPorDia(filters: AccionesPorDiaFilters): Promise<AccionesPorDia[]> {
  return api.get<AccionesPorDia[]>('/api/v1/auditoria/metricas/acciones-por-dia', filters as Record<string, unknown>);
}

export async function getEstadosComunicacion(filters: EstadosComunicacionFilters): Promise<EstadoComunicacion[]> {
  return api.get<EstadoComunicacion[]>('/api/v1/auditoria/metricas/estados-comunicacion', filters as Record<string, unknown>);
}

export async function getInteracciones(filters: InteraccionesFilters): Promise<InteraccionDocente[]> {
  return api.get<InteraccionDocente[]>('/api/v1/auditoria/metricas/interacciones', filters as Record<string, unknown>);
}
