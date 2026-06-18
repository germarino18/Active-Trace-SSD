import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { LiquidacionHistorialItem, LiquidacionKPIs, LiquidacionPeriodo } from '../types/liquidaciones';
import type { CerrarLiquidacionData, LiquidacionFilters } from '../services/liquidaciones.service';
import * as liquidacionesService from '../services/liquidaciones.service';

export function useLiquidacion(filters: LiquidacionFilters) {
  return useQuery<LiquidacionPeriodo>({
    queryKey: ['liquidacion', filters],
    queryFn: () => liquidacionesService.getLiquidacion(filters),
    enabled: !!filters.periodo,
  });
}

export function useLiquidacionKPIs(periodo: string) {
  return useQuery<LiquidacionKPIs>({
    queryKey: ['liquidacion-kpis', periodo],
    queryFn: () => liquidacionesService.getLiquidacionKPIs(periodo),
    enabled: !!periodo,
  });
}

export function useCerrarLiquidacion() {
  const queryClient = useQueryClient();

  return useMutation<LiquidacionPeriodo, Error, CerrarLiquidacionData>({
    mutationFn: (data) => liquidacionesService.cerrarLiquidacion(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['liquidacion'] });
      queryClient.invalidateQueries({ queryKey: ['liquidacion-kpis'] });
      queryClient.invalidateQueries({ queryKey: ['liquidacion-historial'] });
    },
  });
}

export function useHistorial() {
  return useQuery<LiquidacionHistorialItem[]>({
    queryKey: ['liquidacion-historial'],
    queryFn: () => liquidacionesService.getHistorial(),
  });
}
