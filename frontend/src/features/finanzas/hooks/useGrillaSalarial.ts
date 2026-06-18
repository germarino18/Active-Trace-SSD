import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { SalarioBase, PlusSalarial, SalarioBaseFormData, PlusFormData } from '../types/grilla-salarial';
import * as grillaSalarialService from '../services/grilla-salarial.service';

export function useSalariosBase() {
  return useQuery<SalarioBase[]>({
    queryKey: ['salarios-base'],
    queryFn: () => grillaSalarialService.getSalariosBase(),
  });
}

export function usePlus() {
  return useQuery<PlusSalarial[]>({
    queryKey: ['plus'],
    queryFn: () => grillaSalarialService.getPlus(),
  });
}

export function useCrearSalarioBase() {
  const queryClient = useQueryClient();
  return useMutation<SalarioBase, Error, SalarioBaseFormData>({
    mutationFn: (data) => grillaSalarialService.crearSalarioBase(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salarios-base'] });
    },
  });
}

export function useEditarSalarioBase() {
  const queryClient = useQueryClient();
  return useMutation<SalarioBase, Error, { id: string; data: SalarioBaseFormData }>({
    mutationFn: ({ id, data }) => grillaSalarialService.actualizarSalarioBase(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salarios-base'] });
    },
  });
}

export function useCrearPlus() {
  const queryClient = useQueryClient();
  return useMutation<PlusSalarial, Error, PlusFormData>({
    mutationFn: (data) => grillaSalarialService.crearPlus(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plus'] });
    },
  });
}

export function useEditarPlus() {
  const queryClient = useQueryClient();
  return useMutation<PlusSalarial, Error, { id: string; data: PlusFormData }>({
    mutationFn: ({ id, data }) => grillaSalarialService.actualizarPlus(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plus'] });
    },
  });
}
