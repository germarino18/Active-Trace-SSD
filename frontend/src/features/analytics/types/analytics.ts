export interface AtrasadosPorCohorte {
  fecha: string;
  cohorte: string;
  total_atrasados: number;
  total_alumnos: number;
  porcentaje: number;
}

export interface DistribucionNotas {
  rango: string;
  cantidad: number;
}

export interface PrediccionAbandono {
  alumno_id: string;
  alumno_nombre: string;
  materia: string;
  promedio: number;
  atrasos: number;
  riesgo: 'bajo' | 'medio' | 'alto';
}

export interface DashboardKpi {
  total_alumnos: number;
  total_atrasados_actual: number;
  promedio_general: number;
  alumnos_en_riesgo: { bajo: number; medio: number; alto: number };
  tendencia_atrasados_ultimo_mes: Array<{ fecha: string; total: number }>;
  total_materias: number;
}

export interface AnalyticsDashboardFilters {
  fecha_desde?: string;
  fecha_hasta?: string;
  carrera_id?: string;
  cohorte_id?: string;
  materia_id?: string;
  dictado_id?: string;
  riesgo?: 'bajo' | 'medio' | 'alto';
}
