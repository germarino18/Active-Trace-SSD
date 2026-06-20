/**
 * TDD Tasks 9, 10 — AtrasadosGeneralPage: rename + group-by-alumno.
 * 9.1 RED: heading reads "Desaprobados/Atrasados".
 * 10.1 RED: groups rows by alumno, materias comma-separated.
 */
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useAtrasadosGeneralProfesor: vi.fn(),
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  useDictadoNombre: vi.fn(),
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
  invalidateDictadoDerived: vi.fn(),
}));

import { useAtrasadosGeneralProfesor } from '@/features/profesor/hooks/useProfesor';
import { AtrasadosGeneralPage } from '@/features/academico/pages/AtrasadosGeneralPage';

const mockUseAtrasados = vi.mocked(useAtrasadosGeneralProfesor);

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

// Ana García appears in TWO dictados / materias
const crossMateriaData = [
  { entrada_padron_id: 'ep1', nombre: 'Ana', apellido: 'García', dictado_id: 'd1', materia_nombre: 'Matemáticas', actividades_sin_entrega: ['Tarea 1'] },
  { entrada_padron_id: 'ep1', nombre: 'Ana', apellido: 'García', dictado_id: 'd2', materia_nombre: 'Física', actividades_sin_entrega: ['TP Final'] },
  { entrada_padron_id: 'ep2', nombre: 'Carlos', apellido: 'López', dictado_id: 'd1', materia_nombre: 'Matemáticas', actividades_sin_entrega: ['Parcial 1'] },
];

describe('AtrasadosGeneralPage — Desaprobados/Atrasados + grouping', () => {
  beforeEach(() => vi.clearAllMocks());

  it('9.1 — heading reads "Desaprobados/Atrasados" (not "Alumnos Atrasados")', async () => {
    mockUseAtrasados.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAtrasadosGeneralProfesor>);
    renderPage();
    await waitFor(() => expect(screen.getByText('Desaprobados/Atrasados')).toBeInTheDocument());
    expect(screen.queryByText('Alumnos Atrasados')).not.toBeInTheDocument();
  });

  it('10.1 — groups by alumno: one row per alumno, materias comma-separated', async () => {
    mockUseAtrasados.mockReturnValue({ data: crossMateriaData, isLoading: false, isError: false } as ReturnType<typeof useAtrasadosGeneralProfesor>);
    renderPage();

    await waitFor(() => expect(screen.getByTestId('atrasados-table')).toBeInTheDocument());

    // Ana García should appear ONCE with both materias comma-separated
    const rows = screen.getAllByRole('row');
    // rows[0] = header, rows[1..] = data rows
    const dataRows = rows.slice(1);
    expect(dataRows.length).toBe(2); // Ana + Carlos (not 3 separate rows)

    expect(screen.getByText('García, Ana')).toBeInTheDocument();
    expect(screen.getByText('Matemáticas, Física')).toBeInTheDocument();
    expect(screen.getByText('López, Carlos')).toBeInTheDocument();
  });

  it('10.2 — TRIANGULATE: single entry remains one row with single materia', async () => {
    mockUseAtrasados.mockReturnValue({
      data: [crossMateriaData[0]],
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useAtrasadosGeneralProfesor>);
    renderPage();

    await waitFor(() => expect(screen.getByTestId('atrasados-table')).toBeInTheDocument());
    const rows = screen.getAllByRole('row').slice(1);
    expect(rows.length).toBe(1);
    expect(screen.getByText('García, Ana')).toBeInTheDocument();
    expect(screen.getByText('Matemáticas')).toBeInTheDocument();
  });

  it('10.3 — materia filter renders when multiple materias present', async () => {
    mockUseAtrasados.mockReturnValue({ data: crossMateriaData, isLoading: false, isError: false } as ReturnType<typeof useAtrasadosGeneralProfesor>);
    renderPage();
    // We just verify the filter select renders for multi-materia data
    await waitFor(() => expect(screen.getByLabelText('Filtrar por materia')).toBeInTheDocument());
  });

  it('shows empty state when no data', async () => {
    mockUseAtrasados.mockReturnValue({ data: [], isLoading: false, isError: false } as ReturnType<typeof useAtrasadosGeneralProfesor>);
    renderPage();
    await waitFor(() => expect(screen.getByTestId('empty-state')).toBeInTheDocument());
  });
});
