export type RolSalarial = 'PROFESOR' | 'TUTOR' | 'NEXO' | 'COORDINADOR';

export interface SalarioBase {
  id: string;
  rol: RolSalarial;
  importe: number;
  vigencia_desde: string;
  vigencia_hasta?: string;
}

export interface PlusSalarial {
  id: string;
  clave: string;
  rol: RolSalarial;
  descripcion: string;
  importe: number;
  vigencia_desde: string;
  vigencia_hasta?: string;
}

export interface SalarioBaseFormData {
  rol: RolSalarial;
  importe: number;
  vigencia_desde: string;
  vigencia_hasta?: string;
}

export interface PlusFormData {
  clave: string;
  rol: RolSalarial;
  descripcion: string;
  importe: number;
  vigencia_desde: string;
  vigencia_hasta?: string;
}
