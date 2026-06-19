export interface ProfileResponse {
  id: string;
  tenant_id: string;
  nombre: string;
  apellidos: string;
  email: string;
  cuil: string | null;
  dni: string | null;
  cbu: string | null;
  alias_cbu: string | null;
  banco: string | null;
  regional: string | null;
  legajo: string | null;
  legajo_profesional: string | null;
  facturador: boolean;
  estado: 'Activo' | 'Inactivo';
}

export interface ProfilePatchRequest {
  nombre?: string;
  apellidos?: string;
  dni?: string;
  banco?: string;
  cbu?: string;
  alias_cbu?: string;
  regional?: string;
  legajo_profesional?: string;
  facturador?: boolean;
}
