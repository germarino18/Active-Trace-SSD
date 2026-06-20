import { describe, it, expect, vi } from 'vitest';
import * as api from '@/shared/services/api';

vi.mock('@/shared/services/api', () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
}));

const { getUsuarios, getUsuario, crearUsuario, editarUsuario } = await import(
  '@/features/admin/services/usuarios.service'
);

const usuarioResponse = {
  id: '1', tenant_id: 't1', user_id: 'u1',
  nombre: 'Juan', apellidos: 'Pérez',
  banco: null, regional: null, legajo: null, legajo_profesional: null,
  facturador: false, estado: 'Activo', deleted_at: false,
};

describe('usuarios.service', () => {
  it('getUsuarios calls api.get with /api/admin/usuarios', async () => {
    vi.mocked(api.get).mockResolvedValue([usuarioResponse]);
    await getUsuarios();
    expect(api.get).toHaveBeenCalledWith('/api/admin/usuarios', undefined);
  });

  it('getUsuarios passes filters as params', async () => {
    vi.mocked(api.get).mockResolvedValue([usuarioResponse]);
    await getUsuarios({ estado: 'Activo', q: 'test', offset: 0, limit: 25 });
    expect(api.get).toHaveBeenCalledWith('/api/admin/usuarios', {
      estado: 'Activo', q: 'test', offset: 0, limit: 25,
    });
  });

  it('getUsuario calls api.get with /api/admin/usuarios/{id}', async () => {
    vi.mocked(api.get).mockResolvedValue(usuarioResponse);
    await getUsuario('1');
    expect(api.get).toHaveBeenCalledWith('/api/admin/usuarios/1');
  });

  it('crearUsuario calls api.post with /api/admin/usuarios', async () => {
    vi.mocked(api.post).mockResolvedValue(usuarioResponse);
    const data = { user_id: 'u1', nombre: 'Juan', apellidos: 'Pérez' };
    await crearUsuario(data);
    expect(api.post).toHaveBeenCalledWith('/api/admin/usuarios', data);
  });

  it('editarUsuario calls api.patch with /api/admin/usuarios/{id}', async () => {
    const patchMock = vi.mocked(api.patch).mockResolvedValue(usuarioResponse);
    await editarUsuario('1', { nombre: 'Juan Carlos' });
    expect(patchMock).toHaveBeenCalledWith('/api/admin/usuarios/1', { nombre: 'Juan Carlos' });
  });
});
