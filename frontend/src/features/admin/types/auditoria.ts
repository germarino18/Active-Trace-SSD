export interface RegistroAuditoria {
  id: string;
  fecha_hora: string;
  actor_id: string;
  actor_nombre: string | null;
  impersonado_id?: string | null;
  materia_id?: string | null;
  materia_nombre?: string | null;
  accion: string;
  detalle?: Record<string, unknown> | null;
  filas_afectadas?: number | null;
  ip?: string | null;
  user_agent?: string | null;
}

export interface AuditoriaResponse {
  items: RegistroAuditoria[];
  total: number;
  offset: number;
  limit: number;
}

export interface AuditoriaFilters {
  fecha_desde?: string;
  fecha_hasta?: string;
  materia_id?: string;
  usuario_id?: string;
  accion?: string;
  offset?: number;
  limit?: number;
}
