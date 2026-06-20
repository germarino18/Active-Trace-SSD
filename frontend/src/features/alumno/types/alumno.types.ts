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
  cuerpo: string;
  severidad: string;
  inicio_en: string;
  fin_en: string;
  requiere_ack: boolean;
  acknowledged: boolean;
  fecha_publicacion: string;
  vigencia_hasta: string | null;
  created_at: string;
  updated_at: string;
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
  remitente_id: string;
  remitente_nombre: string;
  asunto: string;
  ultimo_mensaje: string;
  ultima_fecha: string;
  no_leido: boolean;
}

export interface MensajeHilo {
  id: string;
  remitente_id: string;
  remitente_nombre: string;
  contenido: string;
  fecha_hora: string;
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
