import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as avisosService from '../services/avisos.service';
import type { Aviso, AvisosResponse } from '../types';
import type { AvisoParams, CrearAvisoData, ActualizarAvisoData } from '../services/avisos.service';

export function useAvisos(params?: AvisoParams) {
  return useQuery<AvisosResponse>({
    queryKey: ['avisos', params],
    queryFn: () => avisosService.getAvisos(params),
  });
}

export function useAviso(id: string | undefined) {
  return useQuery<Aviso>({
    queryKey: ['avisos', id],
    queryFn: () => avisosService.getAviso(id!),
    enabled: !!id,
  });
}

export function useCrearAviso() {
  const queryClient = useQueryClient();
  return useMutation<Aviso, Error, CrearAvisoData>({
    mutationFn: (data) => avisosService.crearAviso(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos'] });
    },
  });
}

export function useActualizarAviso() {
  const queryClient = useQueryClient();
  return useMutation<Aviso, Error, { id: string; data: ActualizarAvisoData }>({
    mutationFn: ({ id, data }) => avisosService.actualizarAviso(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos'] });
    },
  });
}

export function useEliminarAviso() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => avisosService.eliminarAviso(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos'] });
    },
  });
}

export function useConfirmarAck() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (avisoId) => avisosService.confirmarAck(avisoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos'] });
    },
  });
}
