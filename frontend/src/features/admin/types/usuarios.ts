export interface Usuario {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  rol: string;
  activo: boolean;
  created_at: string;
}

export interface UsuariosResponse {
  items: Usuario[];
  total: number;
}

export interface CrearUsuarioData {
  nombre: string;
  apellido: string;
  email: string;
  rol: string;
  activo?: boolean;
}

export interface EditarUsuarioData {
  nombre?: string;
  apellido?: string;
  email?: string;
  rol?: string;
  activo?: boolean;
}

export interface UsuarioFilters {
  rol?: string;
  activo?: boolean;
  q?: string;
  offset?: number;
  limit?: number;
}
