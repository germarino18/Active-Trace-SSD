import { useMutation, useQuery } from '@tanstack/react-query';
import * as comunicacionService from '../services/comunicacion.service';
import type { ComunicacionPreviewResponse } from '../types';

export function usePreviewComunicacion(materiaId: string) {
  return useMutation<ComunicacionPreviewResponse, Error, string[]>({
    mutationFn: (studentIds) => comunicacionService.getPreview(materiaId, studentIds),
  });
}

export function useEnviarComunicacion() {
  return useMutation<{ comunicacion_id: string }, Error, { materiaId: string; studentIds: string[] }>({
    mutationFn: ({ materiaId, studentIds }) => comunicacionService.enviarComunicacion(materiaId, studentIds),
  });
}

export function useStatusComunicacion(comunicacionId: string | null) {
  return useQuery({
    queryKey: ['comunicacion-status', comunicacionId],
    queryFn: () => comunicacionService.getStatus(comunicacionId!),
    enabled: !!comunicacionId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data?.terminal) return false;
      return 3000;
    },
  });
}
