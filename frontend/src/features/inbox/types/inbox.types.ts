export interface HiloResumen {
  id: string;
  remitente: string;
  asunto: string;
  ultimo_mensaje: string;
  fecha: string;
  leido: boolean;
}

export interface Mensaje {
  id: string;
  remitente: string;
  contenido: string;
  fecha: string;
}

export interface ResponderPayload {
  contenido: string;
}
