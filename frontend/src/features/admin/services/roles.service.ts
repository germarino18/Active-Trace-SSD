import * as api from '@/shared/services/api';
import type { RolCatalogo } from '../hooks/useRoles';

export interface UsuarioRol {
  id: string;
  rol_id: string;
  rol_nombre: string;
  vigencia_desde?: string;
  vigencia_hasta?: string;
}

export async function getRolesUsuario(usuarioId: string): Promise<UsuarioRol[]> {
  return api.get<UsuarioRol[]>(`/api/admin/usuarios/${usuarioId}/roles`);
}

export async function asignarRolUsuario(usuarioId: string, data: { rol_id: string }): Promise<UsuarioRol> {
  return api.post<UsuarioRol>(`/api/admin/usuarios/${usuarioId}/roles`, data);
}

export async function removerRolUsuario(usuarioId: string, rolId: string): Promise<void> {
  return api.del<void>(`/api/admin/usuarios/${usuarioId}/roles/${rolId}`);
}

export { type RolCatalogo };
