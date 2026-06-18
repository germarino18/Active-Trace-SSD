export interface Materia {
  id: string;
  nombre: string;
  codigo: string;
  comision: string;
  carrera: string;
  anio: number;
  cuatrimestre: number;
  umbral: number;
  created_at: string;
  updated_at: string;
}

export interface Alumno {
  id: string;
  legajo: string;
  nombre: string;
  apellido: string;
  email: string;
  comision: string;
  dni?: string;
  carrera?: string;
}

export interface Calificacion {
  id: string;
  alumno_id: string;
  materia_id: string;
  actividad: string;
  nota: number;
  fecha: string;
  estado: CalificacionEstado;
}

export type CalificacionEstado = 'aprobado' | 'desaprobado' | 'ausente' | 'pendiente';

export interface Actividad {
  id: string;
  nombre: string;
  tipo: string;
  fecha_limite?: string;
  calificaciones_count: number;
  selected?: boolean;
}

export interface Comunicacion {
  id: string;
  materia_id: string;
  asunto: string;
  cuerpo: string;
  destinatarios: number;
  created_at: string;
  updated_at: string;
}

export type MensajeStatus = 'Pendiente' | 'Enviando' | 'OK' | 'Fallido' | 'Cancelado';

export interface UmbralMateria {
  materia_id: string;
  porcentaje: number;
  updated_at: string;
}

export interface ImportPreviewResponse {
  materia_id: string;
  actividades: Actividad[];
  alumnos_count: number;
  calificaciones_count: number;
}

export interface AtrasadosResponse {
  materia_id: string;
  umbral: number;
  alumnos: AtrasadoEntry[];
  total: number;
}

export interface AtrasadoEntry {
  alumno: Alumno;
  actividades_pendientes: number;
  nota_actual: number;
  porcentaje: number;
  estado: 'atrasado' | 'al_dia';
}

export interface RankingResponse {
  materia_id: string;
  alumnos: RankingEntry[];
}

export interface RankingEntry {
  alumno: Alumno;
  rank: number;
  aprobadas: number;
  total_actividades: number;
  porcentaje: number;
}

export interface NotasFinalesResponse {
  materia_id: string;
  alumnos: NotaFinalEntry[];
}

export interface NotaFinalEntry {
  alumno: Alumno;
  nota_final: number;
  estado: 'aprobado' | 'desaprobado';
}

export interface ReportesRapidosResponse {
  materia_id: string;
  total_alumnos: number;
  en_riesgo: number;
  promedio_completitud: number;
  total_actividades: number;
}

export interface MonitorResponse {
  materia_id: string;
  alumnos: MonitorEntry[];
}

export interface MonitorEntry {
  alumno: Alumno;
  actividades_completadas: number;
  total_actividades: number;
  porcentaje_completitud: number;
  estado: string;
}

export interface EntregasResponse {
  materia_id: string;
  entregas: EntregaEntry[];
}

export interface EntregaEntry {
  alumno: Alumno;
  actividad: string;
  fecha_entrega: string;
  estado: string;
}

export interface ComunicacionPreviewResponse {
  comunicacion_id: string;
  asunto: string;
  cuerpo: string;
  destinatarios: ComunicacionDestinatario[];
}

export interface ComunicacionDestinatario {
  alumno: Alumno;
  asunto: string;
  cuerpo: string;
}

export interface ComunicacionStatusResponse {
  comunicacion_id: string;
  mensajes: MensajeStatusEntry[];
  terminal: boolean;
}

export interface MensajeStatusEntry {
  alumno: Alumno;
  status: MensajeStatus;
  error?: string;
  updated_at: string;
}
