import * as api from '@/shared/services/api';
import type { AtrasadosPorCohorte, DistribucionNotas, PrediccionAbandono, DashboardKpi, AnalyticsDashboardFilters } from '../types/analytics';

export async function getDashboard(): Promise<DashboardKpi> {
  return api.get<DashboardKpi>('/api/admin/analytics/dashboard');
}

export async function getAtrasadosPorCohorte(filters: Partial<AnalyticsDashboardFilters>): Promise<AtrasadosPorCohorte[]> {
  return api.get<AtrasadosPorCohorte[]>('/api/admin/analytics/tendencias/atrasados-por-cohorte', filters as Record<string, unknown>);
}

export async function getDistribucionNotas(filters: Partial<AnalyticsDashboardFilters>): Promise<DistribucionNotas[]> {
  return api.get<DistribucionNotas[]>('/api/admin/analytics/tendencias/distribucion-notas', filters as Record<string, unknown>);
}

export async function getPrediccionAbandono(filters: Partial<AnalyticsDashboardFilters>): Promise<PrediccionAbandono[]> {
  return api.get<PrediccionAbandono[]>('/api/admin/analytics/prediccion/abandono', filters as Record<string, unknown>);
}
