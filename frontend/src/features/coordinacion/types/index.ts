export type InstanciaEstado = 'Pendiente' | 'Realizado' | 'Cancelado';

export interface Docente {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
}

export interface SlotEncuentro {
  materia_id: string;
  titulo: string;
  dia_semana: number;
  hora_inicio: string;
  hora_fin: string;
  semanas: number;
  url_meet?: string;
}

export interface InstanciaEncuentro {
  id: string;
  materia_id: string;
  materia_nombre: string;
  titulo: string;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  docente_id?: string;
  docente_nombre?: string;
  estado: InstanciaEstado;
  url_meet?: string;
  url_grabacion?: string;
  comentario_interno?: string;
  created_at: string;
  updated_at: string;
}

export interface EncuentrosResponse {
  items: InstanciaEncuentro[];
  total: number;
}

export interface DiaConvocatoria {
  id?: string;
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  slots: number;
  cupo_por_slot: number;
}

export interface Convocatoria {
  id: string;
  materia_id: string;
  materia_nombre: string;
  instancia: number;
  dias: DiaConvocatoria[];
  created_at: string;
  updated_at: string;
}

export interface ReservaColoquio {
  id: string;
  convocatoria_id: string;
  dia_id: string;
  alumno_id: string;
  alumno_nombre: string;
  alumno_legajo: string;
  fecha: string;
  hora: string;
  estado: string;
  nota?: number;
}

export interface MetricasColoquio {
  total_alumnos: number;
  instancias_activas: number;
  reservas_activas: number;
  cupos_libres: number;
}

export interface ColoquiosResponse {
  items: Convocatoria[];
  total: number;
}

export type AvisoScope = 'Global' | 'Materia' | 'Cohorte' | 'Rol';

export type AvisoSeverity = 'info' | 'warning' | 'critical';

export interface Aviso {
  id: string;
  tenant_id: string;
  titulo: string;
  mensaje: string;
  scope: AvisoScope;
  scope_value?: string;
  severidad: AvisoSeverity;
  vigencia_desde: string;
  vigencia_hasta: string;
  requiere_ack: boolean;
  orden: number;
  created_by: string;
  created_at: string;
  updated_at: string;
  total_acks: number;
  ack_count: number;
  user_acked: boolean;
}

export interface AvisosResponse {
  items: Aviso[];
  total: number;
}

export type TareaEstado = 'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada';

export interface ComentarioTarea {
  id: string;
  tarea_id: string;
  autor_id: string;
  autor_nombre: string;
  contenido: string;
  created_at: string;
}

export interface Tarea {
  id: string;
  tenant_id: string;
  titulo: string;
  descripcion: string;
  asignado_id: string;
  asignado_nombre: string;
  asignado_por_id: string;
  asignado_por_nombre: string;
  materia_id?: string;
  materia_nombre?: string;
  cohorte_id?: string;
  estado: TareaEstado;
  razon_cancelacion?: string;
  created_at: string;
  updated_at: string;
  comentarios: ComentarioTarea[];
}

export interface TareasResponse {
  items: Tarea[];
  total: number;
}

// ─── Equipos Docentes ───────────────────────────────────────────
export interface Asignacion {
  id: string;
  docente: Docente;
  materia_id: string;
  materia_nombre: string;
  carrera_id: string;
  carrera_nombre: string;
  cohorte_id: string;
  cohorte_nombre: string;
  rol: 'PROFESOR' | 'TUTOR' | 'NEXO' | 'COORDINADOR';
  vigencia_desde: string;
  vigencia_hasta: string;
  estado: 'Activa' | 'Vencida' | 'Cancelada';
  comisiones: string[];
  created_at: string;
  updated_at: string;
}

export interface Equipo {
  materia_id: string;
  materia_nombre: string;
  carrera_id: string;
  carrera_nombre: string;
  cohorte_id: string;
  cohorte_nombre: string;
  miembros: Asignacion[];
}

export interface AsignacionesResponse {
  asignaciones: Asignacion[];
  total: number;
}

// ─── Programas y Fechas Académicas ───────────────────────────

export type TipoFechaAcademica = 'Parcial' | 'TP' | 'Coloquio';

export interface ProgramaMateria {
  id: string;
  tenant_id: string;
  materia_id: string;
  materia_nombre: string;
  carrera_id: string;
  carrera_nombre: string;
  cohorte_id: string;
  cohorte_nombre: string;
  titulo: string;
  archivo_url: string;
  fecha_subida: string;
  created_at: string;
  updated_at: string;
}

export interface FechaAcademica {
  id: string;
  tenant_id: string;
  materia_id: string;
  materia_nombre: string;
  cohorte_id: string;
  cohorte_nombre: string;
  tipo: TipoFechaAcademica;
  instancia: number;
  titulo: string;
  fecha: string;
  created_at: string;
  updated_at: string;
}

export interface ProgramasResponse {
  items: ProgramaMateria[];
  total: number;
}

// ─── Aprobación de Comunicaciones ────────────────────────────

export type EstadoMensajeLote = 'Pendiente' | 'Enviando' | 'OK' | 'Fallido' | 'Cancelado';

export interface DestinatarioLote {
  alumno_id: string;
  nombre: string;
  apellido: string;
  email: string;
  estado: EstadoMensajeLote;
}

export interface LoteComunicacion {
  lote_id: string;
  docente_id: string;
  docente_nombre: string;
  asunto: string;
  cuerpo: string;
  total_destinatarios: number;
  created_at: string;
  destinatarios?: DestinatarioLote[];
}

export interface LotesPendientesResponse {
  items: LoteComunicacion[];
  total: number;
}

// ─── Monitores ──────────────────────────────────────────────

export interface AccionPorDia {
  fecha: string;
  cantidad: number;
}

export interface ComunicacionDocente {
  docente_id: string;
  docente_nombre: string;
  total_enviados: number;
  pendientes: number;
  ok: number;
  fallidos: number;
}

export interface InteraccionDocente {
  docente_id: string;
  docente_nombre: string;
  materia_id: string;
  materia_nombre: string;
  acciones: Record<string, number>;
}

export interface AccionLog {
  id: string;
  usuario_id: string;
  usuario_nombre: string;
  accion: string;
  detalle?: string;
  materia_id?: string;
  materia_nombre?: string;
  created_at: string;
}

export interface MonitorData {
  acciones_por_dia: AccionPorDia[];
  comunicaciones: ComunicacionDocente[];
  interacciones: InteraccionDocente[];
  ultimas_acciones: AccionLog[];
}

export interface MonitorGeneralResponse {
  data: MonitorData;
  total_acciones: number;
}

export interface MonitorCoordinacionResponse {
  data: MonitorData;
  filtros_aplicados: Record<string, unknown>;
}
