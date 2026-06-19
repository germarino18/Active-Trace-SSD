import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as dictadosService from '../services/dictados.service';
import type {
  Dictado,
  DictadosResponse,
  CrearDictadoData,
  ActualizarDictadoData,
  DictadoFilters,
} from '../types/dictados';

export function useDictados(params?: DictadoFilters) {
  return useQuery<DictadosResponse>({
    queryKey: ['dictados', params],
    queryFn: () => dictadosService.getDictados(params),
  });
}

export function useDictado(id: string | undefined) {
  return useQuery<Dictado>({
    queryKey: ['dictados', id],
    queryFn: () => dictadosService.getDictado(id!),
    enabled: !!id,
  });
}

export function useCrearDictado() {
  const queryClient = useQueryClient();
  return useMutation<Dictado, Error, CrearDictadoData>({
    mutationFn: (data) => dictadosService.crearDictado(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['dictados'] }); },
  });
}

export function useActualizarDictado() {
  const queryClient = useQueryClient();
  return useMutation<Dictado, Error, { id: string; data: ActualizarDictadoData }>({
    mutationFn: ({ id, data }) => dictadosService.actualizarDictado(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['dictados'] }); },
  });
}

export function useToggleDictadoEstado() {
  const queryClient = useQueryClient();
  return useMutation<Dictado, Error, string>({
    mutationFn: (id) => dictadosService.toggleDictadoEstado(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['dictados'] }); },
  });
}

export function useEliminarDictado() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => dictadosService.eliminarDictado(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['dictados'] }); },
  });
}
