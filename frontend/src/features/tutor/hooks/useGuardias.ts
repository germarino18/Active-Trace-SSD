import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as guardiaService from '../services/guardia.service';
import type { Guardia, GuardiasResponse, RegistrarGuardiaData } from '../types/tutor.types';

export function useGuardias() {
  return useQuery<GuardiasResponse>({
    queryKey: ['guardias'],
    queryFn: () => guardiaService.getGuardias(),
  });
}

export function useRegistrarGuardia() {
  const queryClient = useQueryClient();
  return useMutation<Guardia, Error, RegistrarGuardiaData>({
    mutationFn: (data) => guardiaService.registrarGuardia(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guardias'] });
    },
  });
}
