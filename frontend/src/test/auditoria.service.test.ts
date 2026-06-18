import { describe, it, expect, vi } from 'vitest';
import * as api from '@/shared/services/api';

vi.mock('@/shared/services/api', () => ({
  get: vi.fn(),
}));

const { getAuditoriaLog, getAuditoriaRegistro } = await import(
  '@/features/admin/services/auditoria.service'
);

describe('auditoria.service', () => {
  it('getAuditoriaLog calls api.get with /api/v1/auditoria/log and filters', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    const filters = { fecha_desde: '2024-01-01', fecha_hasta: '2024-12-31', offset: 0, limit: 200 };
    await getAuditoriaLog(filters);
    expect(api.get).toHaveBeenCalledWith('/api/v1/auditoria/log', filters);
  });

  it('getAuditoriaLog works with empty filters', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getAuditoriaLog({});
    expect(api.get).toHaveBeenCalledWith('/api/v1/auditoria/log', {});
  });

  it('getAuditoriaLog passes tipo_accion filter', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    const filters = { tipo_accion: 'crear', limit: 50 };
    await getAuditoriaLog(filters);
    expect(api.get).toHaveBeenCalledWith('/api/v1/auditoria/log', filters);
  });

  it('getAuditoriaRegistro calls api.get with /api/v1/auditoria/log/{id}', async () => {
    vi.mocked(api.get).mockResolvedValue({
      id: '1', fecha: '2024-01-01', usuario_nombre: 'Admin', tipo_accion: 'crear',
    });
    await getAuditoriaRegistro('1');
    expect(api.get).toHaveBeenCalledWith('/api/v1/auditoria/log/1');
  });

  it('getAuditoriaRegistro returns a single RegistroAuditoria', async () => {
    const mockRegistro = {
      id: 'r1', fecha: '2024-06-15T10:30:00Z', usuario_nombre: 'Juan Pérez',
      materia_nombre: 'Matemática', tipo_accion: 'crear', registros_afectados: 5,
      ip_origen: '192.168.1.1', agente_usuario: 'Mozilla/5.0',
      detalle: { campo: 'nombre', valor_anterior: 'MAT', valor_nuevo: 'MAT-101' },
    };
    vi.mocked(api.get).mockResolvedValue(mockRegistro);
    const result = await getAuditoriaRegistro('r1');
    expect(result).toEqual(mockRegistro);
  });
});
