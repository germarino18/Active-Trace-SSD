/**
 * TDD Tasks 4.6 / 4.7 — dual invalidation on actividad create/edit/delete.
 *
 * Tests the hooks directly (not the page) with a real QueryClient so
 * invalidateQueries calls can be observed without mocking the hook boundary.
 *
 * EXACT query keys (read from useProfesor.ts + invalidateDictadoDerived):
 *   actividades:      ['profesor', 'actividades', dictadoId]
 *   per-dictado atrasados: ['profesor', 'atrasados', dictadoId]
 *   cross-materia atrasados: ['profesor', 'atrasados-general']
 *   metricas:         ['profesor', 'metricas', dictadoId]
 *   dashboard:        ['profesor', 'dashboard']
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient } from '@tanstack/react-query';

// Mock the service module so no real HTTP calls are made
vi.mock('@/features/profesor/services/profesor.service', () => ({
  crearActividad: vi.fn().mockResolvedValue({ id: 'newact', nombre: 'Nueva', tipo: 'tarea', fecha_limite: null }),
  editarActividad: vi.fn().mockResolvedValue({ id: 'act1', nombre: 'Tarea 1', tipo: 'tarea', fecha_limite: '2026-01-15' }),
  eliminarActividad: vi.fn().mockResolvedValue(undefined),
  getActividadesDictado: vi.fn().mockResolvedValue([]),
  getDictadoMetricas: vi.fn().mockResolvedValue({}),
  getProfesorDashboard: vi.fn().mockResolvedValue({}),
  getAtrasadosProfesor: vi.fn().mockResolvedValue([]),
  getAtrasadosGeneralProfesor: vi.fn().mockResolvedValue([]),
}));

// We import the hook functions directly and call them via renderHook
import { renderHook, act } from '@testing-library/react';
import { QueryClientProvider } from '@tanstack/react-query';
import { createElement } from 'react';
import {
  useMutationCrearActividad,
  useMutationEditarActividad,
  useMutationEliminarActividad,
} from '@/features/profesor/hooks/useProfesor';

const DICTADO_ID = 'test-dictado-1';

function makeWrapper(qc: QueryClient) {
  return ({ children }: { children: React.ReactNode }) =>
    createElement(QueryClientProvider, { client: qc }, children);
}

describe('useProfesor actividad mutations — dual invalidation (tasks 4.6 / 4.7)', () => {
  let qc: QueryClient;
  let invalidateSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    vi.clearAllMocks();
    qc = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
    invalidateSpy = vi.spyOn(qc, 'invalidateQueries');
  });

  it('4.6-hook/crear — useMutationCrearActividad invalidates actividades AND atrasados (dual) on success', async () => {
    const { result } = renderHook(
      () => useMutationCrearActividad(DICTADO_ID),
      { wrapper: makeWrapper(qc) },
    );

    await act(async () => {
      await result.current.mutateAsync({ nombre: 'Nueva', tipo: 'tarea', fecha_limite: null });
    });

    const keys = invalidateSpy.mock.calls.map((c) => JSON.stringify(c[0]?.queryKey));

    // Actividades query
    expect(keys).toContain(JSON.stringify(['profesor', 'actividades', DICTADO_ID]));
    // Per-dictado atrasados (from invalidateDictadoDerived)
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados', DICTADO_ID]));
    // Cross-materia atrasados (from invalidateDictadoDerived)
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados-general']));
  });

  it('4.7-hook/editar — useMutationEditarActividad invalidates actividades AND atrasados (dual) on success', async () => {
    const { result } = renderHook(
      () => useMutationEditarActividad(DICTADO_ID),
      { wrapper: makeWrapper(qc) },
    );

    await act(async () => {
      await result.current.mutateAsync({
        actividadId: 'act1',
        data: { fecha_limite: '2026-01-15' },
      });
    });

    const keys = invalidateSpy.mock.calls.map((c) => JSON.stringify(c[0]?.queryKey));

    // Actividades query
    expect(keys).toContain(JSON.stringify(['profesor', 'actividades', DICTADO_ID]));
    // Per-dictado atrasados (dual invalidation required by D3)
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados', DICTADO_ID]));
    // Cross-materia atrasados
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados-general']));
  });

  it('4.8-hook/eliminar — useMutationEliminarActividad invalidates actividades AND atrasados (dual) on success', async () => {
    const { result } = renderHook(
      () => useMutationEliminarActividad(DICTADO_ID),
      { wrapper: makeWrapper(qc) },
    );

    await act(async () => {
      await result.current.mutateAsync('act1');
    });

    const keys = invalidateSpy.mock.calls.map((c) => JSON.stringify(c[0]?.queryKey));

    // Actividades query
    expect(keys).toContain(JSON.stringify(['profesor', 'actividades', DICTADO_ID]));
    // Per-dictado atrasados
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados', DICTADO_ID]));
    // Cross-materia atrasados
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados-general']));
  });
});
