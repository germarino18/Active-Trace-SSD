export interface Dictado {
  id: string;
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  materia_nombre?: string;
  carrera_nombre?: string;
  cohorte_nombre?: string;
  estado: string;
  vig_desde?: string;
  vig_hasta?: string;
}

export interface DictadosResponse {
  items: Dictado[];
  total: number;
}

export interface CrearDictadoData {
  materia_id: string;
  carrera_id: string;
  cohorte_id: string;
  vig_desde?: string;
  vig_hasta?: string;
}

export interface ActualizarDictadoData {
  materia_id?: string;
  carrera_id?: string;
  cohorte_id?: string;
  vig_desde?: string;
  vig_hasta?: string;
}

export interface DictadoFilters {
  activa?: boolean;
  q?: string;
  vigente?: boolean;
}
