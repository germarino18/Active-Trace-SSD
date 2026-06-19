import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as estructuraService from '../services/estructura.service';
import type {
  Carrera,
  CarrerasResponse,
  Cohorte,
  CohortesResponse,
  Materia,
  MateriasResponse,
  Evaluacion,
  EvaluacionesResponse,
  CrearCarreraData,
  ActualizarCarreraData,
  CrearCohorteData,
  ActualizarCohorteData,
  CrearMateriaData,
  ActualizarMateriaData,
  CrearEvaluacionData,
} from '../types';

// ─── Carreras ──────────────────────────────────────────────────

export function useCarreras(params?: { activa?: boolean; q?: string }) {
  return useQuery<CarrerasResponse>({
    queryKey: ['carreras', params],
    queryFn: () => estructuraService.getCarreras(params),
  });
}

export function useCrearCarrera() {
  const queryClient = useQueryClient();
  return useMutation<Carrera, Error, CrearCarreraData>({
    mutationFn: (data) => estructuraService.crearCarrera(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['carreras'] }); },
  });
}

export function useActualizarCarrera() {
  const queryClient = useQueryClient();
  return useMutation<Carrera, Error, { id: string; data: ActualizarCarreraData }>({
    mutationFn: ({ id, data }) => estructuraService.actualizarCarrera(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['carreras'] }); },
  });
}

export function useEliminarCarrera() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => estructuraService.eliminarCarrera(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['carreras'] }); },
  });
}

export function useToggleCarreraEstado() {
  const queryClient = useQueryClient();
  return useMutation<Carrera, Error, string>({
    mutationFn: (id) => estructuraService.toggleCarreraEstado(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['carreras'] }); },
  });
}

// ─── Cohortes ──────────────────────────────────────────────────

export function useCohortes(params?: { activa?: boolean; q?: string }) {
  return useQuery<CohortesResponse>({
    queryKey: ['cohortes', params],
    queryFn: () => estructuraService.getCohortes(params),
  });
}

export function useCrearCohorte() {
  const queryClient = useQueryClient();
  return useMutation<Cohorte, Error, CrearCohorteData>({
    mutationFn: (data) => estructuraService.crearCohorte(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['cohortes'] }); },
  });
}

export function useActualizarCohorte() {
  const queryClient = useQueryClient();
  return useMutation<Cohorte, Error, { id: string; data: ActualizarCohorteData }>({
    mutationFn: ({ id, data }) => estructuraService.actualizarCohorte(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['cohortes'] }); },
  });
}

export function useEliminarCohorte() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => estructuraService.eliminarCohorte(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['cohortes'] }); },
  });
}

export function useToggleCohorteEstado() {
  const queryClient = useQueryClient();
  return useMutation<Cohorte, Error, string>({
    mutationFn: (id) => estructuraService.toggleCohorteEstado(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['cohortes'] }); },
  });
}

// ─── Materias ──────────────────────────────────────────────────

export function useMaterias(params?: { activa?: boolean; q?: string }) {
  return useQuery<MateriasResponse>({
    queryKey: ['materias', params],
    queryFn: () => estructuraService.getMaterias(params),
  });
}

export function useCrearMateria() {
  const queryClient = useQueryClient();
  return useMutation<Materia, Error, CrearMateriaData>({
    mutationFn: (data) => estructuraService.crearMateria(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['materias'] }); },
  });
}

export function useActualizarMateria() {
  const queryClient = useQueryClient();
  return useMutation<Materia, Error, { id: string; data: ActualizarMateriaData }>({
    mutationFn: ({ id, data }) => estructuraService.actualizarMateria(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['materias'] }); },
  });
}

export function useToggleMateriaEstado() {
  const queryClient = useQueryClient();
  return useMutation<Materia, Error, string>({
    mutationFn: (id) => estructuraService.toggleMateriaEstado(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['materias'] }); },
  });
}

// ─── Programas ─────────────────────────────────────────────────

export function useSubirPrograma() {
  const queryClient = useQueryClient();
  return useMutation<{ id: string; archivo_url: string }, Error, { materiaId: string; file: File; titulo: string }>({
    mutationFn: ({ materiaId, file, titulo }) => estructuraService.subirPrograma(materiaId, file, titulo),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['materias'] }); },
  });
}

// ─── Evaluaciones ──────────────────────────────────────────────

export function useEvaluaciones(materiaId?: string) {
  return useQuery<EvaluacionesResponse>({
    queryKey: ['evaluaciones', materiaId],
    queryFn: () => estructuraService.getEvaluaciones(materiaId),
    enabled: !!materiaId,
  });
}

export function useCrearEvaluacion() {
  const queryClient = useQueryClient();
  return useMutation<Evaluacion, Error, CrearEvaluacionData>({
    mutationFn: (data) => estructuraService.crearEvaluacion(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['evaluaciones'] }); },
  });
}
