import { describe, it, expect, vi } from 'vitest';
import * as api from '@/shared/services/api';

vi.mock('@/shared/services/api', () => ({
  get: vi.fn(),
}));

const { getAuditoriaLog } = await import(
  '@/features/admin/services/auditoria.service'
);

describe('auditoria.service', () => {
  it('getAuditoriaLog calls api.get with /api/v1/auditoria/log and filters', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0, offset: 0, limit: 200 });
    const filters = { fecha_desde: '2024-01-01', fecha_hasta: '2024-12-31', offset: 0, limit: 200 };
    await getAuditoriaLog(filters);
    expect(api.get).toHaveBeenCalledWith('/api/v1/auditoria/log', filters);
  });

  it('getAuditoriaLog works with empty filters', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0, offset: 0, limit: 200 });
    await getAuditoriaLog({});
    expect(api.get).toHaveBeenCalledWith('/api/v1/auditoria/log', {});
  });

  it('getAuditoriaLog passes accion filter', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0, offset: 0, limit: 50 });
    const filters = { accion: 'USUARIO_CREAR', limit: 50 };
    await getAuditoriaLog(filters);
    expect(api.get).toHaveBeenCalledWith('/api/v1/auditoria/log', filters);
  });
});
