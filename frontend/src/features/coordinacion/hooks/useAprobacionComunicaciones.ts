import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as aprobacionService from '../services/aprobacion-comunicaciones.service';
import type { LotesPendientesResponse } from '../types';

export const LOTES_PENDIENTES_QUERY_KEY = ['comunicaciones-lotes-pendientes'] as const;

export function useLotesPendientes() {
  return useQuery<LotesPendientesResponse>({
    queryKey: LOTES_PENDIENTES_QUERY_KEY,
    queryFn: () => aprobacionService.getLotesPendientes(),
    staleTime: 30_000,
  });
}

export function useLotesPendientesCount() {
  const { data } = useLotesPendientes();
  return data?.total ?? 0;
}

export function useAprobarLote() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (loteId) => aprobacionService.aprobarLote(loteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LOTES_PENDIENTES_QUERY_KEY });
    },
  });
}

export function useCancelarLote() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (loteId) => aprobacionService.cancelarLote(loteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LOTES_PENDIENTES_QUERY_KEY });
    },
  });
}
