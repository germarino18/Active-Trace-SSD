import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as equiposService from '../services/equipos.service';
import type { Asignacion, AsignacionesResponse, Docente } from '../types';
import type {
  ActualizarAsignacionData,
  AsignacionMasivaData,
  AsignacionMasivaResponse,
  ClonarEquipoData,
  ClonarEquipoResponse,
  CrearAsignacionData,
  EquiposFilters,
  ModificarVigenciaData,
} from '../services/equipos.service';

export function useMisEquipos() {
  return useQuery<AsignacionesResponse>({
    queryKey: ['mis-equipos'],
    queryFn: () => equiposService.getMisEquipos(),
  });
}

export function useEquipos(params?: EquiposFilters) {
  return useQuery<AsignacionesResponse>({
    queryKey: ['equipos', params],
    queryFn: () => equiposService.getEquipos(params),
    enabled: !!params,
  });
}

export function useDocentes() {
  return useQuery<Docente[]>({
    queryKey: ['docentes'],
    queryFn: () => equiposService.getDocentes(),
  });
}

export function useCrearAsignacion() {
  const queryClient = useQueryClient();

  return useMutation<Asignacion, Error, CrearAsignacionData>({
    mutationFn: (data) => equiposService.crearAsignacion(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos'] });
      queryClient.invalidateQueries({ queryKey: ['mis-equipos'] });
    },
  });
}

export function useActualizarAsignacion() {
  const queryClient = useQueryClient();

  return useMutation<Asignacion, Error, { id: string; data: ActualizarAsignacionData }>({
    mutationFn: ({ id, data }) => equiposService.actualizarAsignacion(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos'] });
    },
  });
}

export function useEliminarAsignacion() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (id) => equiposService.eliminarAsignacion(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos'] });
      queryClient.invalidateQueries({ queryKey: ['mis-equipos'] });
    },
  });
}

export function useAsignacionMasiva() {
  const queryClient = useQueryClient();

  return useMutation<AsignacionMasivaResponse, Error, AsignacionMasivaData>({
    mutationFn: (data) => equiposService.asignacionMasiva(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos'] });
    },
  });
}

export function useClonarEquipo() {
  const queryClient = useQueryClient();

  return useMutation<ClonarEquipoResponse, Error, ClonarEquipoData>({
    mutationFn: (data) => equiposService.clonarEquipo(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos'] });
    },
  });
}

export function useModificarVigencia() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, ModificarVigenciaData>({
    mutationFn: (data) => equiposService.modificarVigencia(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos'] });
    },
  });
}
