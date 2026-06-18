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

export interface MetricasDashboard {
  total_docentes_activos: number;
  total_comunicaciones: number;
  comunicaciones_ok: number;
  comunicaciones_fallidas: number;
}
