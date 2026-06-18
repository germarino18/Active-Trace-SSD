import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as liquidacionesService from '@/features/finanzas/services/liquidaciones.service';

const mockGet = vi.fn();
const mockPost = vi.fn();
const mockAxiosGet = vi.fn();

vi.mock('@/shared/services/api', () => ({
  __esModule: true,
  default: {
    get: (...args: unknown[]) => mockAxiosGet(...args),
  },
  get: (...args: unknown[]) => mockGet(...args),
  post: (...args: unknown[]) => mockPost(...args),
}));

beforeEach(() => {
  vi.clearAllMocks();
});

describe('liquidaciones.service', () => {
  describe('getLiquidacion', () => {
    it('calls api.get with correct URL and params', async () => {
      const expectedData = { periodo: '2025-01', segmento: 'general', docentes: [], total_docentes: 0, monto_total: 0, cerrada: false };
      mockGet.mockResolvedValue(expectedData);

      const result = await liquidacionesService.getLiquidacion({ periodo: '2025-01', segmento: 'general' });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/liquidaciones', { periodo: '2025-01', segmento: 'general' });
      expect(result).toEqual(expectedData);
    });
  });

  describe('getLiquidacionKPIs', () => {
    it('calls correct endpoint with periodo', async () => {
      const expectedKPIs = { total_docentes: 10, monto_total: 500000, facturas_pendientes: 2, periodos_cerrados: 3 };
      mockGet.mockResolvedValue(expectedKPIs);

      const result = await liquidacionesService.getLiquidacionKPIs('2025-01');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/liquidaciones/kpis', { periodo: '2025-01' });
      expect(result).toEqual(expectedKPIs);
    });
  });

  describe('cerrarLiquidacion', () => {
    it('calls api.post with correct data', async () => {
      const expectedResponse = { periodo: '2025-01', segmento: 'general', docentes: [], total_docentes: 1, monto_total: 600000, cerrada: true };
      mockPost.mockResolvedValue(expectedResponse);

      const result = await liquidacionesService.cerrarLiquidacion({ periodo: '2025-01' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/liquidaciones/cerrar', { periodo: '2025-01' });
      expect(result).toEqual(expectedResponse);
    });
  });

  describe('getHistorial', () => {
    it('calls correct endpoint', async () => {
      const expectedHistorial = [{ periodo: '2024-12', cerrada_en: '2024-12-15T10:00:00Z', total_docentes: 10, monto_total: 5000000 }];
      mockGet.mockResolvedValue(expectedHistorial);

      const result = await liquidacionesService.getHistorial();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/liquidaciones/historial');
      expect(result).toEqual(expectedHistorial);
    });
  });
});
