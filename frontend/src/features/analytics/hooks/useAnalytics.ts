import { useQuery } from '@tanstack/react-query';
import * as analyticsService from '../services/analytics.service';
import type { AtrasadosPorCohorte, DistribucionNotas, PrediccionAbandono, DashboardKpi, AnalyticsDashboardFilters } from '../types/analytics';

export function useDashboard() {
  return useQuery<DashboardKpi>({
    queryKey: ['analytics-dashboard'],
    queryFn: () => analyticsService.getDashboard(),
    staleTime: 30_000,
  });
}

export function useAtrasadosPorCohorte(filters: Partial<AnalyticsDashboardFilters>) {
  return useQuery<AtrasadosPorCohorte[]>({
    queryKey: ['analytics-atrasados-por-cohorte', filters],
    queryFn: () => analyticsService.getAtrasadosPorCohorte(filters),
    staleTime: 30_000,
  });
}

export function useDistribucionNotas(filters: Partial<AnalyticsDashboardFilters>) {
  return useQuery<DistribucionNotas[]>({
    queryKey: ['analytics-distribucion-notas', filters],
    queryFn: () => analyticsService.getDistribucionNotas(filters),
    staleTime: 30_000,
  });
}

export function usePrediccionAbandono(filters: Partial<AnalyticsDashboardFilters>) {
  return useQuery<PrediccionAbandono[]>({
    queryKey: ['analytics-prediccion-abandono', filters],
    queryFn: () => analyticsService.getPrediccionAbandono(filters),
    staleTime: 30_000,
  });
}
