/**
 * AtrasadosGeneralPage — updated tests for the new cross-materia endpoint.
 *
 * The page now uses GET /api/v1/profesor/atrasados (via useAtrasadosGeneralProfesor hook)
 * which returns AtrasadoGeneral[] directly — no more per-materia fetching.
 */
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock the profesor hook (new endpoint)
vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useAtrasadosGeneralProfesor: vi.fn(),
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
  useEquipoDictado: vi.fn(),
  useAvisosMios: vi.fn(),
  useMutationCrearAviso: vi.fn(),
  useColoquiosMios: vi.fn(),
  useAlumnosDisponibles: vi.fn(),
  useMisTareasProfesor: vi.fn(),
  useMutationCambiarEstadoTareaProfesor: vi.fn(),
}));

import { useAtrasadosGeneralProfesor } from '@/features/profesor/hooks/useProfesor';
import { AtrasadosGeneralPage } from '@/features/academico/pages/AtrasadosGeneralPage';

const mockUseAtrasados = vi.mocked(useAtrasadosGeneralProfesor);

const sampleAtrasados = [
  {
    entrada_padron_id: 'ep1',
    nombre: 'Ana',
    apellido: 'García',
    dictado_id: 'd1',
    materia_nombre: 'Matemáticas',
    actividades_sin_entrega: ['Tarea 1', 'Parcial 2'],
  },
  {
    entrada_padron_id: 'ep2',
    nombre: 'Carlos',
    apellido: 'López',
    dictado_id: 'd2',
    materia_nombre: 'Física',
    actividades_sin_entrega: ['TP Final'],
  },
];

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderPage() {
  return render(
    <QueryClientProvider client={makeQueryClient()}>
      <MemoryRouter>
        <AtrasadosGeneralPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AtrasadosGeneralPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('3.4 — renders combined table when atrasados present (grouped by alumno)', async () => {
    mockUseAtrasados.mockReturnValue({
      data: sampleAtrasados,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosGeneralProfesor>);

    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId('atrasados-table')).toBeInTheDocument();
    });

    // Grouped view: one row per alumno, materia names in the Materias cell
    expect(screen.getByText('García, Ana')).toBeInTheDocument();
    // Materia names appear in both filter dropdown and table rows — use getAllByText
    expect(screen.getAllByText('Matemáticas').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('López, Carlos')).toBeInTheDocument();
    expect(screen.getAllByText('Física').length).toBeGreaterThanOrEqual(1);
    // Note: per-activity detail (Tarea 1, Parcial 2, TP Final) is no longer in the
    // grouped view — the breakdown collapses (D7 accepted tradeoff).
  });

  it('3.5 — shows empty state when no atrasados across all materias', async () => {
    mockUseAtrasados.mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosGeneralProfesor>);

    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    expect(screen.getByText(/No hay alumnos atrasados/)).toBeInTheDocument();
  });

  it('shows filter dropdown when multiple materias', async () => {
    mockUseAtrasados.mockReturnValue({
      data: sampleAtrasados,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosGeneralProfesor>);

    renderPage();

    await waitFor(() => {
      expect(screen.getByLabelText('Filtrar por materia')).toBeInTheDocument();
    });
  });

  it('hides filter when only one materia', async () => {
    mockUseAtrasados.mockReturnValue({
      data: [sampleAtrasados[0]],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosGeneralProfesor>);

    renderPage();

    // Only one materia → no dropdown
    expect(screen.queryByLabelText('Filtrar por materia')).not.toBeInTheDocument();
  });

  it('shows loading spinner while fetching', () => {
    mockUseAtrasados.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as ReturnType<typeof useAtrasadosGeneralProfesor>);

    renderPage();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
