import * as api from '@/shared/services/api';
import type { Usuario, UsuariosResponse, CrearUsuarioData, EditarUsuarioData, UsuarioFilters } from '../types';

export async function getUsuarios(params?: UsuarioFilters): Promise<UsuariosResponse> {
  return api.get<UsuariosResponse>('/api/v1/usuarios', params as Record<string, unknown>);
}

export async function getUsuario(id: string): Promise<Usuario> {
  return api.get<Usuario>(`/api/v1/usuarios/${id}`);
}

export async function crearUsuario(data: CrearUsuarioData): Promise<Usuario> {
  return api.post<Usuario>('/api/v1/usuarios', data);
}

export async function editarUsuario(id: string, data: EditarUsuarioData): Promise<Usuario> {
  return api.put<Usuario>(`/api/v1/usuarios/${id}`, data);
}
