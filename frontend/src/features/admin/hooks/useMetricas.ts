import { useQuery } from '@tanstack/react-query';
import * as metricasService from '../services/metricas.service';
import type { AccionesPorDiaFilters, EstadosComunicacionFilters, InteraccionesFilters } from '../services/metricas.service';
import type { AccionesPorDia, EstadoComunicacion, InteraccionDocente, MetricasResponse } from '../types/metricas';

export function useMetricasDashboard() {
  return useQuery<MetricasResponse>({
    queryKey: ['metricas-dashboard'],
    queryFn: () => metricasService.getMetricasDashboard(),
  });
}

export function useAccionesPorDia(filters: AccionesPorDiaFilters) {
  return useQuery<AccionesPorDia[]>({
    queryKey: ['metricas-acciones-por-dia', filters],
    queryFn: () => metricasService.getAccionesPorDia(filters),
  });
}

export function useEstadosComunicacion(filters: EstadosComunicacionFilters) {
  return useQuery<EstadoComunicacion[]>({
    queryKey: ['metricas-estados-comunicacion', filters],
    queryFn: () => metricasService.getEstadosComunicacion(filters),
  });
}

export function useInteracciones(filters: InteraccionesFilters) {
  return useQuery<InteraccionDocente[]>({
    queryKey: ['metricas-interacciones', filters],
    queryFn: () => metricasService.getInteracciones(filters),
  });
}
