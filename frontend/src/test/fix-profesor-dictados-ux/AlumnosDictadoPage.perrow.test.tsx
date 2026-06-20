/**
 * TDD Task 6.3 / 6.4 — AlumnosDictadoPage: per-row delete button.
 * RED: each row shows a "Dar de baja" button that calls useMutationQuitarAlumno.
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  useDictadoNombre: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationAgregarAlumnosBulk: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useMutationQuitarAlumnosBulk: vi.fn(),
  useAlumnosDisponibles: vi.fn(),
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
  useEquipoDictado: vi.fn(),
  useAvisosMios: vi.fn(),
  useMutationCrearAviso: vi.fn(),
  useColoquiosMios: vi.fn(),
  useAtrasadosGeneralProfesor: vi.fn(),
  useMisTareasProfesor: vi.fn(),
  useMutationCambiarEstadoTareaProfesor: vi.fn(),
  invalidateDictadoDerived: vi.fn(),
}));

import {
  usePadronDictado,
  useMutationAgregarAlumnosBulk,
  useMutationQuitarAlumno,
  useMutationQuitarAlumnosBulk,
  useAlumnosDisponibles,
} from '@/features/profesor/hooks/useProfesor';
import { AlumnosDictadoPage } from '@/features/profesor/pages/AlumnosDictadoPage';

const mockUsePadron = vi.mocked(usePadronDictado);
const mockAgregarBulk = vi.mocked(useMutationAgregarAlumnosBulk);
const mockQuitarSingle = vi.mocked(useMutationQuitarAlumno);
const mockQuitarBulk = vi.mocked(useMutationQuitarAlumnosBulk);
const mockAlumnosDisponibles = vi.mocked(useAlumnosDisponibles);

const defaultMutation = {
  mutateAsync: vi.fn().mockResolvedValue(undefined),
  isPending: false,
  isError: false,
  isSuccess: false,
  reset: vi.fn(),
};

const samplePadron = [
  { id: 'e1', nombre: 'Juan', apellidos: 'Pérez', email: 'jp@test.com', comision: 'A' },
  { id: 'e2', nombre: 'Ana', apellidos: 'García', email: null, comision: null },
];

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/dictados/d1/alumnos']}>
        <Routes>
          <Route path="/dictados/:dictadoId/alumnos" element={<AlumnosDictadoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AlumnosDictadoPage — per-row delete', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAgregarBulk.mockReturnValue(defaultMutation as ReturnType<typeof useMutationAgregarAlumnosBulk>);
    mockQuitarBulk.mockReturnValue(defaultMutation as ReturnType<typeof useMutationQuitarAlumnosBulk>);
    mockQuitarSingle.mockReturnValue(defaultMutation as ReturnType<typeof useMutationQuitarAlumno>);
    mockAlumnosDisponibles.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAlumnosDisponibles>);
    mockUsePadron.mockReturnValue({ data: samplePadron, isLoading: false, isError: false } as ReturnType<typeof usePadronDictado>);
  });

  it('6.3 — renders a per-row delete button for each alumno', () => {
    renderPage();
    const buttons = screen.getAllByRole('button', { name: /dar de baja/i });
    // one per row
    expect(buttons.length).toBe(samplePadron.length);
  });

  it('6.4 — clicking row delete shows confirm/cancel, confirming calls mutateAsync', async () => {
    const mutateAsync = vi.fn().mockResolvedValue(undefined);
    mockQuitarSingle.mockReturnValue({
      ...defaultMutation,
      mutateAsync,
    } as ReturnType<typeof useMutationQuitarAlumno>);

    renderPage();

    // Click the first row's delete button
    const btn = screen.getByRole('button', { name: /dar de baja juan pérez/i });
    fireEvent.click(btn);

    // Confirm button should appear
    const confirmBtn = screen.getByRole('button', { name: /confirmar baja juan pérez/i });
    expect(confirmBtn).toBeInTheDocument();
    const cancelBtn = screen.getByRole('button', { name: /cancelar/i });
    expect(cancelBtn).toBeInTheDocument();

    fireEvent.click(confirmBtn);
    await waitFor(() => expect(mutateAsync).toHaveBeenCalledWith('e1'));
  });

  it('6.5 — TRIANGULATE: cancel hides confirm without calling mutateAsync', () => {
    renderPage();

    const btn = screen.getByRole('button', { name: /dar de baja juan pérez/i });
    fireEvent.click(btn);

    expect(screen.getByRole('button', { name: /confirmar baja juan pérez/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /cancelar/i }));

    expect(screen.queryByRole('button', { name: /confirmar baja juan pérez/i })).not.toBeInTheDocument();
    expect(defaultMutation.mutateAsync).not.toHaveBeenCalled();
  });
});
