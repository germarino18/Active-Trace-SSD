export interface MetricasResponse {
  total_alumnos: number;
  alumnos_activos: number;
  porcentaje_riesgo: number;
  promedio_progreso: number;
  total_docentes: number;
  total_materias_activas: number;
  total_carreras_activas: number;
}

export interface AccionesPorDia {
  fecha: string;
  total: number;
}

export interface EstadoComunicacion {
  estado: string;
  cantidad: number;
  docente_nombre?: string;
  materia_nombre?: string;
}

export interface InteraccionDocente {
  docente_nombre: string;
  tipo_accion: string;
  cantidad: number;
}
