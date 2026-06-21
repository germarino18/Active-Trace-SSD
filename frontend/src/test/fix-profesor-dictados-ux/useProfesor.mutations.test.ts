/**
 * TDD: Task 8 — invalidateDictadoDerived + useDictadoNombre
 * Tests that the shared helper invalidates the correct keys, and that the
 * nombre hook derives the right display string from metricas data.
 */
import { describe, it, expect, vi } from 'vitest';
import type { QueryClient } from '@tanstack/react-query';

// Test the pure helper by importing it directly
import { invalidateDictadoDerived } from '@/features/profesor/hooks/useProfesor';

describe('invalidateDictadoDerived', () => {
  it('invalidates metricas, dashboard, atrasados, atrasados-general for given dictadoId', () => {
    const queryClient = {
      invalidateQueries: vi.fn(),
    } as unknown as QueryClient;

    invalidateDictadoDerived(queryClient, 'dictado-123');

    const calls = (queryClient.invalidateQueries as ReturnType<typeof vi.fn>).mock.calls;
    const keys = calls.map((c: [{ queryKey: unknown[] }]) => JSON.stringify(c[0].queryKey));

    expect(keys).toContain(JSON.stringify(['profesor', 'metricas', 'dictado-123']));
    expect(keys).toContain(JSON.stringify(['profesor', 'dashboard']));
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados', 'dictado-123']));
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados-general']));
  });

  it('TRIANGULATE: works with a different dictadoId', () => {
    const queryClient = {
      invalidateQueries: vi.fn(),
    } as unknown as QueryClient;

    invalidateDictadoDerived(queryClient, 'dictado-abc');

    const calls = (queryClient.invalidateQueries as ReturnType<typeof vi.fn>).mock.calls;
    const keys = calls.map((c: [{ queryKey: unknown[] }]) => JSON.stringify(c[0].queryKey));

    expect(keys).toContain(JSON.stringify(['profesor', 'metricas', 'dictado-abc']));
    expect(keys).toContain(JSON.stringify(['profesor', 'atrasados', 'dictado-abc']));
  });
});
