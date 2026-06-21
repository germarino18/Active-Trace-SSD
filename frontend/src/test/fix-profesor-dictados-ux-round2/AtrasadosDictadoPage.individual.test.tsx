/**
 * TDD RED — Task 3.2 / 3.4
 * Per-row individual comunicado in AtrasadosDictadoPage.
 *
 * Assertions:
 * 3.2  Clicking "Comunicado individual" on a row opens ComunicadoFlexibleForm
 *      pre-scoped to that single alumno.
 * 3.4a Approval gate: submit calls useMutationComunicadoFlexible, not a new mutation.
 * 3.4b Edge case: no per-row button when the group is empty (hidden group).
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// ------- mock the hook module -------
vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationAgregarAlumnosBulk: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useMutationQuitarAlumnosBulk: vi.fn(),
  useActividadesDictado: vi.fn(),
  useCalificacionesDictado: vi.fn(),
  useMutationEditarCalificacion: vi.fn(),
  useMutationCrearActividad: vi.fn(),
  useMutationEliminarActividad: vi.fn(),
  useMutationSubirCalificacionesCsv: vi.fn(),
  useMutationRegistrarCalificacion: vi.fn(),
  useAtrasadosProfesor: vi.fn(),
  useMutationComunicadoAtrasadoNull: vi.fn(),
  useMutationComunicadoAtrasados: vi.fn(),
  useMutationComunicadoFlexible: vi.fn(),
  useEquipoDictado: vi.fn(),
  useAvisosMios: vi.fn(),
  useMutationCrearAviso: vi.fn(),
  useColoquiosMios: vi.fn(),
  useAlumnosDisponibles: vi.fn(),
  useAtrasadosGeneralProfesor: vi.fn(),
  useMisTareasProfesor: vi.fn(),
  useMutationCambiarEstadoTareaProfesor: vi.fn(),
}));

import {
  useAtrasadosProfesor,
  useActividadesDictado,
  useMutationComunicadoAtrasados,
  useMutationComunicadoFlexible,
} from '@/features/profesor/hooks/useProfesor';
import { AtrasadosDictadoPage } from '@/features/profesor/pages/AtrasadosDictadoPage';

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });

const mockUseAtrasados = vi.mocked(useAtrasadosProfesor);
const mockUseActividades = vi.mocked(useActividadesDictado);
const mockMutationComunicado = vi.mocked(useMutationComunicadoAtrasados);
const mockMutationFlexible = vi.mocked(useMutationComunicadoFlexible);

const mutateAsyncFlexible = vi.fn().mockResolvedValue({ total: 1, lote_id: 'lot1' });

const defaultMutation = {
  mutateAsync: vi.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
};

// alumno_id in AtrasadoProfesor IS the entrada_padron_id (backend sets it as entrada.id)
const sampleData = [
  {
    alumno_id: 'ep-ana',
    nombre: 'Ana',
    apellido: 'García',
    estado: 'atrasado' as const,
    subtipo: 'desaprobado' as const,
    actividades_desaprobadas: 2,
    actividades_atrasado_null: 0,
  },
  {
    alumno_id: 'ep-carlos',
    nombre: 'Carlos',
    apellido: 'López',
    estado: 'atrasado' as const,
    subtipo: 'atrasado_null' as const,
    actividades_desaprobadas: 0,
    actividades_atrasado_null: 1,
  },
];

function renderPage() {
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/profesor/dictados/d1/atrasados']}>
        <Routes>
          <Route path="/profesor/dictados/:dictadoId/atrasados" element={<AtrasadosDictadoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AtrasadosDictadoPage — per-row individual comunicado (tasks 3.2 / 3.4)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationComunicado.mockReturnValue(defaultMutation as ReturnType<typeof useMutationComunicadoAtrasados>);
    mockMutationFlexible.mockReturnValue({
      mutateAsync: mutateAsyncFlexible,
      isPending: false,
      isError: false,
      isSuccess: false,
    } as ReturnType<typeof useMutationComunicadoFlexible>);
    mockUseActividades.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useActividadesDictado>);
    mockUseAtrasados.mockReturnValue({ data: sampleData, isLoading: false, isError: false } as ReturnType<typeof useAtrasadosProfesor>);
  });

  // Task 3.2: per-row button exists and opens ComunicadoFlexibleForm
  it('3.2a — each atrasado row has a "Comunicado individual" button', () => {
    renderPage();
    // There should be per-row individual comunicado buttons
    const buttons = screen.getAllByText('Comunicado individual');
    expect(buttons.length).toBeGreaterThanOrEqual(1);
  });

  it('3.2b — clicking "Comunicado individual" on Ana opens the flexible form scoped to Ana', async () => {
    renderPage();
    // Find the per-row button for Ana (desaprobado group)
    const individualBtns = screen.getAllByText('Comunicado individual');
    fireEvent.click(individualBtns[0]);

    // ComunicadoFlexibleForm should appear with Ana's name in the title
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
    // The dialog title should reference Ana García
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-label', expect.stringContaining('García'));
  });

  // Task 3.4a: submit calls useMutationComunicadoFlexible (same approval gate)
  it('3.4a — submitting per-row form calls useMutationComunicadoFlexible, not a new mutation', async () => {
    renderPage();
    const individualBtns = screen.getAllByText('Comunicado individual');
    fireEvent.click(individualBtns[0]);

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    // Fill required fields
    fireEvent.change(screen.getByLabelText(/asunto/i), { target: { value: 'Test asunto' } });
    fireEvent.change(screen.getByLabelText(/cuerpo/i), { target: { value: 'Test cuerpo del mensaje' } });

    // Submit
    fireEvent.click(screen.getByText('Enviar comunicado'));

    await waitFor(() => {
      // The flexible mutation must have been called
      expect(mutateAsyncFlexible).toHaveBeenCalledOnce();
    });

    // The payload must include this alumno as a destinatario
    const [callPayload] = mutateAsyncFlexible.mock.calls[0];
    expect(callPayload.destinatarios).toHaveLength(1);
    expect(callPayload.destinatarios[0].entrada_padron_id).toBe('ep-ana');
  });

  // Task 3.4b: edge case — empty data shows no per-row buttons
  it('3.4b — when no atrasados, no "Comunicado individual" buttons appear', () => {
    mockUseAtrasados.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAtrasadosProfesor>);
    renderPage();
    expect(screen.queryByText('Comunicado individual')).not.toBeInTheDocument();
  });
});
