import * as api from '@/shared/services/api';
import { normalizeListResponse } from './helpers';
import type { Usuario, UsuariosResponse, CrearUsuarioData, EditarUsuarioData, UsuarioFilters } from '../types';

export async function getUsuarios(params?: UsuarioFilters): Promise<UsuariosResponse> {
  const data = await api.get<unknown>('/api/admin/usuarios', params as Record<string, unknown>);
  return normalizeListResponse<Usuario>(data);
}

export async function getUsuario(id: string): Promise<Usuario> {
  return api.get<Usuario>(`/api/admin/usuarios/${id}`);
}

export async function crearUsuario(data: CrearUsuarioData): Promise<Usuario> {
  return api.post<Usuario>('/api/admin/usuarios', data);
}

export async function editarUsuario(id: string, data: EditarUsuarioData): Promise<Usuario> {
  return api.put<Usuario>(`/api/admin/usuarios/${id}`, data);
}
