/**
 * TDD Tasks 3.1 / 3.2 — DictadoDashboardPage shows Materia — Cohorte header.
 * RED: header shows materia_nombre — cohorte_nombre, NOT "Panel del Dictado" nor raw UUID.
 */
import { render, screen } from '@testing-library/react';
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
  invalidateDictadoDerived: vi.fn(),
}));

import { useDictadoMetricas, useDictadoNombre } from '@/features/profesor/hooks/useProfesor';
import { DictadoDashboardPage } from '@/features/profesor/pages/DictadoDashboardPage';

const mockUseDictadoMetricas = vi.mocked(useDictadoMetricas);
const mockUseDictadoNombre = vi.mocked(useDictadoNombre);

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/dictados/d1']}>
        <Routes>
          <Route path="/dictados/:dictadoId" element={<DictadoDashboardPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('DictadoDashboardPage — dictado name header', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('3.1 — renders Materia — Cohorte as the heading (not "Panel del Dictado")', () => {
    mockUseDictadoMetricas.mockReturnValue({
      data: {
        total_alumnos: 10,
        aprobados: 8,
        atrasados: 2,
        total_actividades: 3,
        promedio_general: 7.5,
        sin_datos: 0,
        materia_nombre: 'Matemáticas',
        cohorte_nombre: '2024',
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDictadoMetricas>);
    mockUseDictadoNombre.mockReturnValue('Matemáticas — 2024');

    renderPage();

    expect(screen.getByText('Matemáticas — 2024')).toBeInTheDocument();
    expect(screen.queryByText('Panel del Dictado')).not.toBeInTheDocument();
    // Must NOT show the raw UUID as literal text in heading
    expect(screen.queryByText(/ID: d1/)).not.toBeInTheDocument();
  });

  it('3.2 — TRIANGULATE: different materia/cohorte renders correctly', () => {
    mockUseDictadoMetricas.mockReturnValue({
      data: {
        total_alumnos: 5,
        aprobados: 3,
        atrasados: 2,
        total_actividades: 2,
        promedio_general: null,
        sin_datos: 0,
        materia_nombre: 'Física',
        cohorte_nombre: '2025',
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDictadoMetricas>);
    mockUseDictadoNombre.mockReturnValue('Física — 2025');

    renderPage();

    expect(screen.getByText('Física — 2025')).toBeInTheDocument();
    expect(screen.queryByText('Panel del Dictado')).not.toBeInTheDocument();
  });

  it('3.3 — shows placeholder while loading (not UUID)', () => {
    mockUseDictadoMetricas.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as ReturnType<typeof useDictadoMetricas>);
    mockUseDictadoNombre.mockReturnValue('Cargando…');

    renderPage();

    expect(screen.getByText('Cargando…')).toBeInTheDocument();
    expect(screen.queryByText('Panel del Dictado')).not.toBeInTheDocument();
  });
});
