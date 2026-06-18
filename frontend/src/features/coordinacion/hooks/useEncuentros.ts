import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as encuentrosService from '../services/encuentros.service';
import type { EncuentrosResponse, InstanciaEncuentro } from '../types';
import type { EncuentrosParams, CrearSlotData, CrearEncuentroData, ActualizarInstanciaData } from '../services/encuentros.service';

export function useEncuentros(params?: EncuentrosParams) {
  return useQuery<EncuentrosResponse>({
    queryKey: ['encuentros', params],
    queryFn: () => encuentrosService.getEncuentros(params),
  });
}

export function useEncuentro(id: string | undefined) {
  return useQuery<InstanciaEncuentro>({
    queryKey: ['encuentros', id],
    queryFn: () => encuentrosService.getEncuentro(id!),
    enabled: !!id,
  });
}

export function useCrearSlotRecurrente() {
  const queryClient = useQueryClient();
  return useMutation<{ instancias: number }, Error, CrearSlotData>({
    mutationFn: (data) => encuentrosService.crearSlotRecurrente(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['encuentros'] });
    },
  });
}

export function useCrearEncuentroUnico() {
  const queryClient = useQueryClient();
  return useMutation<InstanciaEncuentro, Error, CrearEncuentroData>({
    mutationFn: (data) => encuentrosService.crearEncuentroUnico(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['encuentros'] });
    },
  });
}

export function useActualizarInstancia() {
  const queryClient = useQueryClient();
  return useMutation<InstanciaEncuentro, Error, { id: string; data: ActualizarInstanciaData }>({
    mutationFn: ({ id, data }) => encuentrosService.actualizarInstancia(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['encuentros'] });
    },
  });
}

export function useGenerarHtml() {
  return useMutation<string, Error, string>({
    mutationFn: async (id) => {
      const result = await encuentrosService.generarHtml(id);
      return result.html;
    },
  });
}
