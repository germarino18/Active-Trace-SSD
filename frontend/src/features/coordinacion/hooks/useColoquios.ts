import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as coloquiosService from '../services/coloquios.service';
import type { ColoquiosResponse, Convocatoria, MetricasColoquio, ReservaColoquio } from '../types';
import type { CrearConvocatoriaData } from '../services/coloquios.service';

export function useConvocatorias() {
  return useQuery<ColoquiosResponse>({
    queryKey: ['convocatorias'],
    queryFn: () => coloquiosService.getConvocatorias(),
  });
}

export function useConvocatoria(id: string | undefined) {
  return useQuery<Convocatoria>({
    queryKey: ['convocatorias', id],
    queryFn: () => coloquiosService.getConvocatoria(id!),
    enabled: !!id,
  });
}

export function useCrearConvocatoria() {
  const queryClient = useQueryClient();
  return useMutation<Convocatoria, Error, CrearConvocatoriaData>({
    mutationFn: (data) => coloquiosService.crearConvocatoria(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['convocatorias'] });
    },
  });
}

export function useImportarAlumnos() {
  const queryClient = useQueryClient();
  return useMutation<{ alumnos: number }, Error, { convocatoriaId: string; file: File }>({
    mutationFn: ({ convocatoriaId, file }) => coloquiosService.importarAlumnos(convocatoriaId, file),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['convocatorias', variables.convocatoriaId] });
    },
  });
}

export function useMetricas(id: string | undefined) {
  return useQuery<MetricasColoquio>({
    queryKey: ['convocatorias', id, 'metricas'],
    queryFn: () => coloquiosService.getMetricas(id!),
    enabled: !!id,
  });
}

export function useReservarTurno() {
  const queryClient = useQueryClient();
  return useMutation<ReservaColoquio, Error, { convocatoriaId: string; diaId: string }>({
    mutationFn: ({ convocatoriaId, diaId }) => coloquiosService.reservarTurno(convocatoriaId, diaId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['convocatorias'] });
    },
  });
}

export function useResultados(id: string | undefined) {
  return useQuery<ReservaColoquio[]>({
    queryKey: ['convocatorias', id, 'resultados'],
    queryFn: () => coloquiosService.getResultados(id!),
    enabled: !!id,
  });
}
