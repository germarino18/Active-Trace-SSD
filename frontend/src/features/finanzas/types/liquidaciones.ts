export type SegmentoLiquidacion = 'general' | 'nexo' | 'factura';

export interface LiquidacionDocente {
  id: string;
  docente_nombre: string;
  docente_apellido: string;
  rol: string;
  comisiones: number;
  salario_base: number;
  plus: number;
  total: number;
}

export interface LiquidacionPeriodo {
  periodo: string;
  segmento: SegmentoLiquidacion;
  docentes: LiquidacionDocente[];
  total_docentes: number;
  monto_total: number;
  cerrada: boolean;
}

export interface LiquidacionKPIs {
  total_docentes: number;
  monto_total: number;
  facturas_pendientes: number;
  periodos_cerrados: number;
}

export interface LiquidacionHistorialItem {
  periodo: string;
  cerrada_en: string;
  total_docentes: number;
  monto_total: number;
}
