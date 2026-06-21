/**
 * TDD RED/GREEN/TRIANGULATE — Task 7c
 * Pure helper: getFechaLimiteStatus(fechaLimite: string | null, today: string): 'vencida' | 'proxima' | null
 * Badge rendering: ActividadCard shows status badge inline after ({tipo})
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';

// ---- Pure helper tests (no DOM) ----
import { getFechaLimiteStatus } from '@/features/profesor/utils/fechaLimiteStatus';

describe('getFechaLimiteStatus — pure unit', () => {
  // 7c.2 TRIANGULATE: vencida
  it('returns "vencida" when fecha_limite is before today', () => {
    expect(getFechaLimiteStatus('2020-01-01', '2026-06-20')).toBe('vencida');
  });

  // 7c.2 TRIANGULATE: proxima (within 7 days)
  it('returns "proxima" when fecha_limite is within 7 days from today', () => {
    expect(getFechaLimiteStatus('2026-06-25', '2026-06-20')).toBe('proxima');
  });

  // 7c.2 TRIANGULATE: proxima on exact day
  it('returns "proxima" when fecha_limite is exactly today', () => {
    expect(getFechaLimiteStatus('2026-06-20', '2026-06-20')).toBe('proxima');
  });

  // 7c.2 TRIANGULATE: proxima on boundary (7 days out)
  it('returns "proxima" when fecha_limite is exactly 7 days from today', () => {
    expect(getFechaLimiteStatus('2026-06-27', '2026-06-20')).toBe('proxima');
  });

  // 7c.2 TRIANGULATE: lejana (>7 days)
  it('returns null when fecha_limite is more than 7 days away', () => {
    expect(getFechaLimiteStatus('2026-12-31', '2026-06-20')).toBe(null);
  });

  // 7c.2 TRIANGULATE: sin fecha
  it('returns null when fecha_limite is null', () => {
    expect(getFechaLimiteStatus(null, '2026-06-20')).toBe(null);
  });
});

// ---- ActividadCard badge rendering tests ----

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useMutationSubirCalificacionesCsv: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false, isError: false })),
  useMutationRegistrarCalificacion: vi.fn(() => ({ mutateAsync: vi.fn(), isPending: false, isError: false })),
}));

vi.mock('@/features/profesor/services/profesor.service', () => ({
  downloadPlantillaCsv: vi.fn(),
}));

import { ActividadCard } from '@/features/profesor/components/ActividadCard';
import type { VirtualActividad } from '@/features/profesor/components/ActividadCard';

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });

function makeAct(fecha_limite: string | null): VirtualActividad {
  return { id: 'act1', nombre: 'Tarea 1', tipo: 'tarea', fecha_limite };
}

const baseProps = {
  dictadoId: 'd1',
  cals: [],
  padron: [],
  editState: null,
  onStartEdit: vi.fn(),
  onSave: vi.fn(),
  onCancelEdit: vi.fn(),
  onChangeEdit: vi.fn(),
  isSaving: false,
  isRegistrando: false,
  onCloseRegistrar: vi.fn(),
};

function renderCard(act: VirtualActividad) {
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>
        <ActividadCard act={act} {...baseProps} />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ActividadCard — fecha_limite badge and position (task 7c.1)', () => {
  it('shows "Vencida" badge when fecha_limite is in the past', () => {
    renderCard(makeAct('2020-01-01'));
    expect(screen.getByText('Vencida')).toBeInTheDocument();
  });

  it('shows "Próxima" badge when fecha_limite is within 7 days', () => {
    renderCard(makeAct('2026-06-25'));
    expect(screen.getByText('Próxima')).toBeInTheDocument();
  });

  it('shows no status badge when fecha_limite is null', () => {
    renderCard(makeAct(null));
    expect(screen.queryByText('Vencida')).not.toBeInTheDocument();
    expect(screen.queryByText('Próxima')).not.toBeInTheDocument();
  });

  it('shows no status badge when fecha_limite is far in the future (lejana)', () => {
    renderCard(makeAct('2030-12-31'));
    expect(screen.queryByText('Vencida')).not.toBeInTheDocument();
    expect(screen.queryByText('Próxima')).not.toBeInTheDocument();
  });

  it('renders fecha_limite text AFTER the tipo in the DOM (not pushed far right)', () => {
    const { container } = renderCard(makeAct('2026-06-25'));
    const header = container.querySelector('.bg-surface-container-low');
    const text = header?.textContent ?? '';
    // "(tarea)" must appear before "Límite:"
    const tipoIdx = text.indexOf('(tarea)');
    const limiteIdx = text.indexOf('Límite:');
    expect(tipoIdx).toBeGreaterThanOrEqual(0);
    expect(limiteIdx).toBeGreaterThan(tipoIdx);
  });
});
