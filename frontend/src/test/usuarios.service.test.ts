import { describe, it, expect, vi } from 'vitest';
import * as api from '@/shared/services/api';

vi.mock('@/shared/services/api', () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
}));

const { getUsuarios, getUsuario, crearUsuario, editarUsuario } = await import(
  '@/features/admin/services/usuarios.service'
);

describe('usuarios.service', () => {
  it('getUsuarios calls api.get with /api/v1/usuarios', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getUsuarios();
    expect(api.get).toHaveBeenCalledWith('/api/v1/usuarios', undefined);
  });

  it('getUsuarios passes filters as params', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getUsuarios({ rol: 'ADMIN', activo: true, q: 'test', offset: 0, limit: 25 });
    expect(api.get).toHaveBeenCalledWith('/api/v1/usuarios', {
      rol: 'ADMIN', activo: true, q: 'test', offset: 0, limit: 25,
    });
  });

  it('getUsuario calls api.get with /api/v1/usuarios/{id}', async () => {
    vi.mocked(api.get).mockResolvedValue({ id: '1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com', rol: 'ADMIN', activo: true, created_at: '2024-01-01' });
    await getUsuario('1');
    expect(api.get).toHaveBeenCalledWith('/api/v1/usuarios/1');
  });

  it('crearUsuario calls api.post with /api/v1/usuarios', async () => {
    vi.mocked(api.post).mockResolvedValue({ id: '1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com', rol: 'ADMIN', activo: true, created_at: '2024-01-01' });
    const data = { nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com', rol: 'ADMIN' };
    await crearUsuario(data);
    expect(api.post).toHaveBeenCalledWith('/api/v1/usuarios', data);
  });

  it('editarUsuario calls api.put with /api/v1/usuarios/{id}', async () => {
    vi.mocked(api.put).mockResolvedValue({ id: '1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com', rol: 'ADMIN', activo: true, created_at: '2024-01-01' });
    await editarUsuario('1', { nombre: 'Juan Carlos' });
    expect(api.put).toHaveBeenCalledWith('/api/v1/usuarios/1', { nombre: 'Juan Carlos' });
  });
});
