export interface Carrera {
  id: string;
  codigo: string;
  nombre: string;
  estado: string;
}

export interface CarreraFilters {
  activa?: boolean;
  q?: string;
}

export interface Cohorte {
  id: string;
  nombre: string;
  anio_inicio: number;
  vigencia_desde: string;
  vigencia_hasta?: string;
  estado: string;
}

export interface CohorteFilters {
  activa?: boolean;
  q?: string;
}

export interface Materia {
  id: string;
  nombre: string;
  codigo?: string;
  estado: string;
  carrera_id?: string;
  carrera_nombre?: string;
  cohorte_id?: string;
  cohorte_nombre?: string;
}

export interface MateriaFilters {
  activa?: boolean;
  q?: string;
}

export interface Evaluacion {
  id: string;
  materia_id: string;
  tipo: 'parcial' | 'tp' | 'coloquio';
  instancia: number;
  fecha: string;
  titulo?: string;
  cohorte_id: string;
}

export interface CarrerasResponse {
  items: Carrera[];
  total: number;
}

export interface CohortesResponse {
  items: Cohorte[];
  total: number;
}

export interface MateriasResponse {
  items: Materia[];
  total: number;
}

export interface EvaluacionesResponse {
  items: Evaluacion[];
  total: number;
}

export interface CrearCarreraData {
  codigo: string;
  nombre: string;
}

export interface ActualizarCarreraData {
  codigo?: string;
  nombre?: string;
}

export interface CrearCohorteData {
  nombre: string;
  anio_inicio: number;
  vigencia_desde: string;
  vigencia_hasta?: string;
}

export interface ActualizarCohorteData {
  nombre?: string;
  anio_inicio?: number;
  vigencia_desde?: string;
  vigencia_hasta?: string;
}

export interface CrearMateriaData {
  nombre: string;
  codigo?: string;
  carrera_id?: string;
  cohorte_id?: string;
}

export interface ActualizarMateriaData {
  nombre?: string;
  codigo?: string;
  carrera_id?: string;
  cohorte_id?: string;
  estado?: string;
}

export interface CrearEvaluacionData {
  materia_id: string;
  tipo: 'parcial' | 'tp' | 'coloquio';
  instancia: number;
  fecha: string;
  titulo?: string;
  cohorte_id: string;
}
