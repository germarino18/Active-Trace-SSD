// Types for the profesor feature

export interface DictadoResumen {
  dictado_id: string;
  materia_id: string;
  materia_nombre: string;
  n_alumnos: number;
}

export interface ProfesorDashboard {
  materias_asignadas: DictadoResumen[];
  total_alumnos: number;
  total_encuentros: number;
  total_atrasados: number;
}

export interface DictadoMetricas {
  total_alumnos: number;
  aprobados: number;
  atrasados: number;
  total_actividades: number;
  promedio_general: number | null;
  sin_datos: number;
}

export interface EntradaPadron {
  id: string;
  nombre: string;
  apellidos: string;
  email: string | null;
  comision: string | null;
}

/** Primary path: pick an existing alumno by usuario_id */
export type AgregarAlumnoByUserId = {
  usuario_id: string;
  comision?: string;
};

/** Fallback path: free-text entry (legacy) */
export type AgregarAlumnoFreeText = {
  nombre: string;
  apellidos: string;
  email?: string;
  comision?: string;
};

export type AgregarAlumnoData = AgregarAlumnoByUserId | AgregarAlumnoFreeText;

/** Alumno available to be added to a dictado padron */
export interface AlumnoDisponible {
  usuario_id: string;
  nombre: string;
  apellidos: string;
  email: string | null;
}

export interface Actividad {
  id: string;
  nombre: string;
  tipo: string;
  fecha_limite: string | null;
}

export interface CalificacionResponse {
  id: string;
  /** entrada_padron_id — identifies the alumno in the padron */
  entrada_padron_id: string;
  dictado_id: string;
  /** actividad name (string) — always present, including legacy imported rows */
  actividad: string;
  /** actividad_id — UUID of the Actividad entity, or null for legacy/imported rows */
  actividad_id: string | null;
  nota_numerica: number | null;
  nota_textual: string | null;
  aprobado: boolean;
  origen: string;
}

export type EstadoAlumno = 'aprobado' | 'atrasado';
export type SubtipoAtrasado = 'desaprobado' | 'atrasado_null' | null;

export interface AtrasadoProfesor {
  alumno_id: string;
  nombre: string;
  apellido: string;
  estado: EstadoAlumno;
  subtipo: SubtipoAtrasado;
  actividades_desaprobadas: number;
  actividades_atrasado_null: number;
}

export interface ComunicadoResult {
  total: number;
  lote_id: string | null;
}

export interface MiembroEquipo {
  usuario_id: string;
  nombre: string;
  apellidos: string;
  rol: string;
  desde: string;
  hasta: string | null;
}

export interface AvisoProfesor {
  id: string;
  tenant_id: string;
  alcance: string;
  materia_id: string | null;
  cohorte_id: string | null;
  rol_destino: string | null;
  severidad: string;
  titulo: string;
  cuerpo: string;
  inicio_en: string;
  fin_en: string;
  orden: number;
  activo: boolean;
  requiere_ack: boolean;
  acknowledged: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Backend `GET /api/v1/profesor/avisos/mios` returns a plain array of AvisoVisibleRead.
 * The `AvisosProfesorResponse` wrapper was a client-side invention — removed.
 * Use `AvisoProfesor[]` directly.
 */
export type AvisosProfesorResponse = AvisoProfesor[];

export interface ColoquioProfesor {
  id: string;
  instancia: string;
  estado: string;
  tipo: string;
  dictado_id: string;
}

export interface EditarCalificacionData {
  nota_numerica?: number | null;
  nota_textual?: string | null;
  aprobado?: boolean | null;
}

export interface ActividadCreate {
  nombre: string;
  tipo: string;
  fecha_limite?: string | null;
}

export interface CsvUploadResult {
  created: number;
  updated: number;
  errors: number;
  total: number;
}

export interface ComunicadoAtrasadosData {
  actividad_id: string;
  subtipo: 'desaprobado' | 'atrasado_null';
  asunto_template: string;
  cuerpo_template: string;
}

export interface AvisoCreate {
  alcance: string;
  materia_id?: string | null;
  cohorte_id?: string | null;
  severidad: 'info' | 'warning' | 'critical';
  titulo: string;
  cuerpo: string;
  inicio_en: string;
  fin_en: string;
  orden: number;
  requiere_ack: boolean;
}

/** Payload for POST /api/v1/actividades/{id}/calificaciones */
export interface RegistrarCalificacionData {
  entrada_padron_id: string;
  nota_numerica?: number | null;
  nota_textual?: string | null;
  aprobado: boolean;
}

/**
 * Cross-materia atrasados entry from GET /api/v1/profesor/atrasados.
 * Each entry = one alumno in one dictado, with their pending activities.
 */
export interface AtrasadoGeneral {
  entrada_padron_id: string;
  nombre: string;
  apellido: string;
  dictado_id: string;
  materia_nombre: string;
  actividades_sin_entrega: string[];
}

/** Tarea as returned by GET /api/v1/tareas/mias (plain array) */
export interface TareaProfesor {
  id: string;
  descripcion: string;
  estado: string;
  materia_id?: string | null;
  asignado_a: string;
  asignado_por: string;
  created_at: string;
  updated_at: string;
}
