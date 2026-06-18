import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as programasService from '../services/programas.service';
import type { ProgramaMateria, FechaAcademica } from '../types';
import type { FechasParams, CrearFechaData, ActualizarFechaData } from '../services/programas.service';

export function useProgramas() {
  return useQuery({
    queryKey: ['programas'],
    queryFn: () => programasService.getProgramas(),
  });
}

export function useCrearPrograma() {
  const queryClient = useQueryClient();
  return useMutation<ProgramaMateria, Error, { file: File; data: Record<string, string> }>({
    mutationFn: ({ file, data }) => programasService.crearPrograma(file, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programas'] });
    },
  });
}

export function useEliminarPrograma() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => programasService.eliminarPrograma(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programas'] });
    },
  });
}

export function useFechasAcademicas(params?: FechasParams) {
  return useQuery({
    queryKey: ['fechas-academicas', params],
    queryFn: () => programasService.getFechasAcademicas(params),
  });
}

export function useCrearFechaAcademica() {
  const queryClient = useQueryClient();
  return useMutation<FechaAcademica, Error, CrearFechaData>({
    mutationFn: (data) => programasService.crearFechaAcademica(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fechas-academicas'] });
    },
  });
}

export function useActualizarFechaAcademica() {
  const queryClient = useQueryClient();
  return useMutation<FechaAcademica, Error, { id: string; data: ActualizarFechaData }>({
    mutationFn: ({ id, data }) => programasService.actualizarFechaAcademica(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fechas-academicas'] });
    },
  });
}

export function useGenerarHtmlFechas() {
  return useMutation({
    mutationFn: ({ materiaId, cohorteId }: { materiaId: string; cohorteId: string }) =>
      programasService.generarHtmlFechas(materiaId, cohorteId),
  });
}
