export type EstadoFactura = 'pendiente' | 'abonada';

export interface Factura {
  id: string;
  docente_id: string;
  docente_nombre: string;
  periodo: string;
  detalle: string;
  archivo_nombre?: string;
  archivo_tamano?: number;
  estado: EstadoFactura;
  datos_pago?: string;
  fecha_carga: string;
}

export interface FacturasResponse {
  items: Factura[];
  total: number;
}

export interface CrearFacturaData {
  docente_id: string;
  periodo: string;
  detalle: string;
  archivo?: File;
}

export interface EditarFacturaData {
  docente_id?: string;
  periodo?: string;
  detalle?: string;
  archivo?: File;
}

export interface FacturaFilters {
  docente?: string;
  estado?: EstadoFactura | '';
  fecha_desde?: string;
  fecha_hasta?: string;
  q?: string;
  offset?: number;
  limit?: number;
}
