export interface HiloResumen {
  id: string;
  remitente_id: string;
  remitente_nombre: string;
  asunto: string;
  ultimo_mensaje: string;
  ultima_fecha: string;
  no_leido: boolean;
}

export interface Mensaje {
  id: string;
  remitente_id: string;
  remitente_nombre: string;
  contenido: string;
  fecha_hora: string;
}

export interface ResponderPayload {
  contenido: string;
}
