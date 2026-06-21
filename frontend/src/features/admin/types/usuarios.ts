export interface Usuario {
  id: string;
  tenant_id: string;
  user_id: string;
  nombre: string;
  apellidos: string;
  banco: string | null;
  regional: string | null;
  legajo: string | null;
  legajo_profesional: string | null;
  facturador: boolean;
  estado: 'Activo' | 'Inactivo';
  deleted_at: boolean;
}

export interface UsuariosResponse {
  items: Usuario[];
  total: number;
}

export interface CrearUsuarioData {
  user_id: string;
  nombre: string;
  apellidos: string;
  dni?: string | null;
  cuil?: string | null;
  cbu?: string | null;
  alias_cbu?: string | null;
  banco?: string | null;
  regional?: string | null;
  legajo?: string | null;
  legajo_profesional?: string | null;
  facturador?: boolean;
}

export interface EditarUsuarioData {
  nombre?: string;
  apellidos?: string;
  dni?: string | null;
  cuil?: string | null;
  cbu?: string | null;
  alias_cbu?: string | null;
  banco?: string | null;
  regional?: string | null;
  legajo?: string | null;
  legajo_profesional?: string | null;
  facturador?: boolean | null;
  estado?: 'Activo' | 'Inactivo' | null;
}

export interface UsuarioFilters {
  estado?: string;
  q?: string;
  offset?: number;
  limit?: number;
}
