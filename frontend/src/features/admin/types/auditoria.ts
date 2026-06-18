export interface RegistroAuditoria {
  id: string;
  fecha: string;
  usuario_nombre: string;
  materia_nombre?: string;
  tipo_accion: string;
  registros_afectados?: number;
  ip_origen?: string;
  agente_usuario?: string;
  detalle?: Record<string, unknown>;
}

export interface AuditoriaResponse {
  items: RegistroAuditoria[];
  total: number;
}

export interface AuditoriaFilters {
  fecha_desde?: string;
  fecha_hasta?: string;
  materia_id?: string;
  usuario_id?: string;
  tipo_accion?: string;
  offset?: number;
  limit?: number;
}
