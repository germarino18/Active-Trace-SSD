import { describe, it, expect, vi } from 'vitest';
import * as api from '@/shared/services/api';

vi.mock('@/shared/services/api', () => ({
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  del: vi.fn(),
  patch: vi.fn(),
  default: { post: vi.fn() },
}));

const {
  getCarreras,
  getCarrera,
  crearCarrera,
  actualizarCarrera,
  eliminarCarrera,
  toggleCarreraEstado,
} = await import('@/features/admin/services/estructura.service');

const {
  getCohortes,
  getCohorte,
  crearCohorte,
  actualizarCohorte,
  eliminarCohorte,
  toggleCohorteEstado,
} = await import('@/features/admin/services/estructura.service');

const {
  getMaterias,
  getMateria,
  crearMateria,
  actualizarMateria,
  toggleMateriaEstado,
  subirPrograma,
  getEvaluaciones,
  crearEvaluacion,
} = await import('@/features/admin/services/estructura.service');

describe('estructura.service - Carreras', () => {
  it('getCarreras calls api.get with /api/v1/carreras', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getCarreras();
    expect(api.get).toHaveBeenCalledWith('/api/v1/carreras', undefined);
  });

  it('getCarreras passes activa param', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getCarreras(true);
    expect(api.get).toHaveBeenCalledWith('/api/v1/carreras', { activa: true });
  });

  it('getCarrera calls api.get with /api/v1/carreras/{id}', async () => {
    vi.mocked(api.get).mockResolvedValue({ id: '1', codigo: 'MAT', nombre: 'Matemática', activa: true });
    await getCarrera('1');
    expect(api.get).toHaveBeenCalledWith('/api/v1/carreras/1');
  });

  it('crearCarrera calls api.post with /api/v1/carreras', async () => {
    vi.mocked(api.post).mockResolvedValue({ id: '1', codigo: 'MAT', nombre: 'Matemática', activa: true });
    await crearCarrera({ codigo: 'MAT', nombre: 'Matemática' });
    expect(api.post).toHaveBeenCalledWith('/api/v1/carreras', { codigo: 'MAT', nombre: 'Matemática' });
  });

  it('actualizarCarrera calls api.put with /api/v1/carreras/{id}', async () => {
    vi.mocked(api.put).mockResolvedValue({ id: '1', codigo: 'MAT', nombre: 'Matemática', activa: true });
    await actualizarCarrera('1', { nombre: 'Matemática II' });
    expect(api.put).toHaveBeenCalledWith('/api/v1/carreras/1', { nombre: 'Matemática II' });
  });

  it('eliminarCarrera calls api.del with /api/v1/carreras/{id}', async () => {
    vi.mocked(api.del).mockResolvedValue(undefined);
    await eliminarCarrera('1');
    expect(api.del).toHaveBeenCalledWith('/api/v1/carreras/1');
  });

  it('toggleCarreraEstado calls api.patch with /api/v1/carreras/{id}/estado', async () => {
    vi.mocked(api.patch).mockResolvedValue({ id: '1', codigo: 'MAT', nombre: 'Matemática', activa: false });
    await toggleCarreraEstado('1');
    expect(api.patch).toHaveBeenCalledWith('/api/v1/carreras/1/estado');
  });
});

describe('estructura.service - Cohortes', () => {
  it('getCohortes calls api.get with /api/v1/cohortes', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getCohortes();
    expect(api.get).toHaveBeenCalledWith('/api/v1/cohortes', undefined);
  });

  it('getCohorte calls api.get with /api/v1/cohortes/{id}', async () => {
    vi.mocked(api.get).mockResolvedValue({ id: '1', nombre: '2024', anio: 2024, vig_desde: '2024-01-01', estado: 'Activa', carrera_id: 'c1' });
    await getCohorte('1');
    expect(api.get).toHaveBeenCalledWith('/api/v1/cohortes/1');
  });

  it('crearCohorte calls api.post with /api/v1/cohortes', async () => {
    vi.mocked(api.post).mockResolvedValue({ id: '1', nombre: '2024', anio: 2024, vig_desde: '2024-01-01', estado: 'Activa', carrera_id: 'c1' });
    await crearCohorte({ carrera_id: 'c1', nombre: '2024', anio: 2024, vig_desde: '2024-01-01' });
    expect(api.post).toHaveBeenCalledWith('/api/v1/cohortes', { carrera_id: 'c1', nombre: '2024', anio: 2024, vig_desde: '2024-01-01' });
  });

  it('actualizarCohorte calls api.put with /api/v1/cohortes/{id}', async () => {
    vi.mocked(api.put).mockResolvedValue({ id: '1', nombre: '2024', anio: 2024, vig_desde: '2024-01-01', estado: 'Activa', carrera_id: 'c1' });
    await actualizarCohorte('1', { nombre: '2025' });
    expect(api.put).toHaveBeenCalledWith('/api/v1/cohortes/1', { nombre: '2025' });
  });

  it('eliminarCohorte calls api.del with /api/v1/cohortes/{id}', async () => {
    vi.mocked(api.del).mockResolvedValue(undefined);
    await eliminarCohorte('1');
    expect(api.del).toHaveBeenCalledWith('/api/v1/cohortes/1');
  });

  it('toggleCohorteEstado calls api.patch with /api/v1/cohortes/{id}/estado', async () => {
    vi.mocked(api.patch).mockResolvedValue({ id: '1', nombre: '2024', anio: 2024, vig_desde: '2024-01-01', estado: 'Inactiva', carrera_id: 'c1' });
    await toggleCohorteEstado('1');
    expect(api.patch).toHaveBeenCalledWith('/api/v1/cohortes/1/estado');
  });
});

describe('estructura.service - Materias', () => {
  it('getMaterias calls api.get with /api/v1/materias', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getMaterias();
    expect(api.get).toHaveBeenCalledWith('/api/v1/materias', undefined);
  });

  it('getMateria calls api.get with /api/v1/materias/{id}', async () => {
    vi.mocked(api.get).mockResolvedValue({ id: '1', nombre: 'Álgebra', activa: true });
    await getMateria('1');
    expect(api.get).toHaveBeenCalledWith('/api/v1/materias/1');
  });

  it('crearMateria calls api.post with /api/v1/materias', async () => {
    vi.mocked(api.post).mockResolvedValue({ id: '1', nombre: 'Álgebra', activa: true });
    await crearMateria({ nombre: 'Álgebra' });
    expect(api.post).toHaveBeenCalledWith('/api/v1/materias', { nombre: 'Álgebra' });
  });

  it('actualizarMateria calls api.put with /api/v1/materias/{id}', async () => {
    vi.mocked(api.put).mockResolvedValue({ id: '1', nombre: 'Álgebra', activa: true });
    await actualizarMateria('1', { nombre: 'Álgebra II' });
    expect(api.put).toHaveBeenCalledWith('/api/v1/materias/1', { nombre: 'Álgebra II' });
  });

  it('toggleMateriaEstado calls api.patch with /api/v1/materias/{id}/estado', async () => {
    vi.mocked(api.patch).mockResolvedValue({ id: '1', nombre: 'Álgebra', activa: false });
    await toggleMateriaEstado('1');
    expect(api.patch).toHaveBeenCalledWith('/api/v1/materias/1/estado');
  });

  it('subirPrograma uses apiClient.post with /api/v1/materias/{id}/programas and multipart', async () => {
    const defaultExport = (await import('@/shared/services/api')).default;
    vi.mocked(defaultExport.post).mockResolvedValue({ data: { id: 'p1', archivo_url: '/uploads/test.pdf' } });
    const file = new File(['dummy'], 'test.pdf', { type: 'application/pdf' });
    const result = await subirPrograma('1', file, 'Programa 2024');
    expect(defaultExport.post).toHaveBeenCalledWith(
      '/api/v1/materias/1/programas',
      expect.any(FormData),
      { headers: { 'Content-Type': 'multipart/form-data' } },
    );
    expect(result).toEqual({ id: 'p1', archivo_url: '/uploads/test.pdf' });
  });

  it('getEvaluaciones calls api.get with /api/v1/evaluaciones', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getEvaluaciones();
    expect(api.get).toHaveBeenCalledWith('/api/v1/evaluaciones', undefined);
  });

  it('getEvaluaciones passes materia_id param', async () => {
    vi.mocked(api.get).mockResolvedValue({ items: [], total: 0 });
    await getEvaluaciones('m1');
    expect(api.get).toHaveBeenCalledWith('/api/v1/evaluaciones', { materia_id: 'm1' });
  });

  it('crearEvaluacion calls api.post with /api/v1/evaluaciones', async () => {
    vi.mocked(api.post).mockResolvedValue({ id: 'e1', materia_id: 'm1', tipo: 'parcial', instancia: 1, fecha: '2024-06-01', cohorte_id: 'c1' });
    const data = { materia_id: 'm1', tipo: 'parcial' as const, instancia: 1, fecha: '2024-06-01', cohorte_id: 'c1' };
    await crearEvaluacion(data);
    expect(api.post).toHaveBeenCalledWith('/api/v1/evaluaciones', data);
  });
});
