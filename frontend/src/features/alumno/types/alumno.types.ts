export interface AlumnoDashboardResponse {
  materias: MateriaDashboardItem[];
  avisos_no_leidos: number;
  comunicaciones_no_leidas: number;
  proximos_coloquios: ProximoColoquioItem[];
  proximas_fechas: ProximaFechaItem[];
}

export interface MateriaDashboardItem {
  id: string;
  nombre: string;
  profesor: string;
  progreso: { aprobadas: number; total: number };
  estado: 'al_dia' | 'atrasado' | 'sin_actividad';
}

export interface ProximoColoquioItem {
  id: string;
  materia_nombre: string;
  fecha: string;
  cupos_restantes: number;
}

export interface ProximaFechaItem {
  id: string;
  materia_nombre: string;
  tipo: string;
  fecha: string;
  descripcion: string;
}

export interface EstadoAcademicoMateria {
  id: string;
  nombre: string;
  profesor: string;
  actividades: ActividadEstado[];
  promedio: number | null;
  condicion: 'regular' | 'libre' | 'promovido';
}

export interface ActividadEstado {
  id: string;
  nombre: string;
  nota: number | null;
  estado: 'aprobado' | 'desaprobado' | 'ausente' | 'pendiente';
}

export interface ConvocatoriaColoquio {
  id: string;
  materia_nombre: string;
  fechas: FechaConCupo[];
  fecha_limite: string;
}

export interface FechaConCupo {
  fecha_id: string;
  fecha: string;
  cupos_restantes: number;
}

export interface ReservaColoquio {
  id: string;
  convocatoria_id: string;
  fecha: string;
  estado: 'Activa' | 'Cancelada';
}

export interface AvisoAlumno {
  id: string;
  titulo: string;
  contenido: string;
  prioridad: number;
  fecha_publicacion: string;
  require_ack: boolean;
  leido: boolean;
  vigencia_hasta: string | null;
}

export interface ProgramaMateria {
  id: string;
  materia_nombre: string;
  programa_nombre: string;
  fecha_publicacion: string;
  referencia_archivo: string | null;
}

export interface FechaAcademica {
  id: string;
  materia_nombre: string;
  tipo: string;
  fecha: string;
  descripcion: string;
}

export interface HiloInbox {
  id: string;
  remitente: string;
  asunto: string;
  ultimo_mensaje: string;
  fecha: string;
  leido: boolean;
}

export interface MensajeHilo {
  id: string;
  remitente: string;
  contenido: string;
  fecha: string;
}

export interface ComunicacionRecibida {
  id: string;
  remitente: string;
  materia_nombre: string;
  asunto: string;
  fecha_envio: string;
  estado: string;
}

export interface ComunicacionDetalle {
  id: string;
  asunto: string;
  cuerpo: string;
  remitente: string;
  materia_nombre: string;
  fecha_envio: string;
  estado_entrega: string;
}
