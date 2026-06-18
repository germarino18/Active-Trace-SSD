import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as tareasService from '../services/tareas.service';
import type { Tarea, TareasResponse, ComentarioTarea } from '../types';
import type { TareaParams, CrearTareaData } from '../services/tareas.service';

export function useMisTareas(params?: TareaParams) {
  return useQuery<TareasResponse>({
    queryKey: ['tareas', 'mias', params],
    queryFn: () => tareasService.getMisTareas(params),
  });
}

export function useTareas(params?: TareaParams) {
  return useQuery<TareasResponse>({
    queryKey: ['tareas', params],
    queryFn: () => tareasService.getTareas(params),
  });
}

export function useTarea(id: string | undefined) {
  return useQuery<Tarea>({
    queryKey: ['tareas', id],
    queryFn: () => tareasService.getTarea(id!),
    enabled: !!id,
  });
}

export function useCrearTarea() {
  const queryClient = useQueryClient();
  return useMutation<Tarea, Error, CrearTareaData>({
    mutationFn: (data) => tareasService.crearTarea(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tareas'] });
    },
  });
}

export function useCambiarEstado() {
  const queryClient = useQueryClient();
  return useMutation<Tarea, Error, { tareaId: string; estado: string; razon?: string }>({
    mutationFn: ({ tareaId, estado, razon }) => tareasService.cambiarEstado(tareaId, estado, razon),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tareas'] });
    },
  });
}

export function useAgregarComentario() {
  const queryClient = useQueryClient();
  return useMutation<ComentarioTarea, Error, { tareaId: string; contenido: string }>({
    mutationFn: ({ tareaId, contenido }) => tareasService.agregarComentario(tareaId, contenido),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tareas'] });
    },
  });
}

export function useDelegarTarea() {
  const queryClient = useQueryClient();
  return useMutation<Tarea, Error, { tareaId: string; nuevoAsignadoId: string }>({
    mutationFn: ({ tareaId, nuevoAsignadoId }) => tareasService.delegarTarea(tareaId, nuevoAsignadoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tareas'] });
    },
  });
}
