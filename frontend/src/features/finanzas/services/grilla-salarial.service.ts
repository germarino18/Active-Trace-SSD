import * as api from '@/shared/services/api';
import type { SalarioBase, PlusSalarial, SalarioBaseFormData, PlusFormData } from '../types/grilla-salarial';

export async function getSalariosBase(): Promise<SalarioBase[]> {
  return api.get<SalarioBase[]>('/api/v1/grilla/salarios-base');
}

export async function crearSalarioBase(data: SalarioBaseFormData): Promise<SalarioBase> {
  return api.post<SalarioBase>('/api/v1/grilla/salarios-base', data);
}

export async function actualizarSalarioBase(id: string, data: SalarioBaseFormData): Promise<SalarioBase> {
  return api.put<SalarioBase>(`/api/v1/grilla/salarios-base/${id}`, data);
}

export async function getPlus(): Promise<PlusSalarial[]> {
  return api.get<PlusSalarial[]>('/api/v1/grilla/plus');
}

export async function crearPlus(data: PlusFormData): Promise<PlusSalarial> {
  return api.post<PlusSalarial>('/api/v1/grilla/plus', data);
}

export async function actualizarPlus(id: string, data: PlusFormData): Promise<PlusSalarial> {
  return api.put<PlusSalarial>(`/api/v1/grilla/plus/${id}`, data);
}
