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
      <MemoryRouter initialEntries={['/profesor/dictados/d1']}>
        <Routes>
          <Route path="/profesor/dictados/:dictadoId" element={<DictadoDashboardPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('DictadoDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default: hook returns a human name (tests that need different can override)
    mockUseDictadoNombre.mockReturnValue('Matemáticas — 2024');
  });

  it('shows loading spinner while fetching metrics', () => {
    mockUseDictadoMetricas.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as ReturnType<typeof useDictadoMetricas>);
    mockUseDictadoNombre.mockReturnValue('Cargando…');

    renderPage();
    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });

  it('renders 6 stat cards when metrics loaded', () => {
    mockUseDictadoMetricas.mockReturnValue({
      data: {
        total_alumnos: 30,
        aprobados: 20,
        atrasados: 5,
        total_actividades: 4,
        promedio_general: 7.25,
        sin_datos: 5,
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDictadoMetricas>);

    renderPage();
    expect(screen.getByText('Total alumnos')).toBeInTheDocument();
    expect(screen.getByText('Aprobados')).toBeInTheDocument();
    // 'Atrasados' appears in both the stat card label and the tab — use getAllByText
    expect(screen.getAllByText('Atrasados').length).toBeGreaterThanOrEqual(1);
    // 'Actividades' appears in stat card label AND tab
    expect(screen.getAllByText('Actividades').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Promedio general')).toBeInTheDocument();
    expect(screen.getByText('Sin datos')).toBeInTheDocument();
  });

  it('formats promedio_general to 2 decimals', () => {
    mockUseDictadoMetricas.mockReturnValue({
      data: {
        total_alumnos: 10,
        aprobados: 8,
        atrasados: 2,
        total_actividades: 3,
        promedio_general: 8.5,
        sin_datos: 0,
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDictadoMetricas>);

    renderPage();
    expect(screen.getByText('8.50')).toBeInTheDocument();
  });

  it('renders 4 tab navigation items (alumnos, actividades, atrasados, equipo)', () => {
    mockUseDictadoMetricas.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useDictadoMetricas>);

    renderPage();
    expect(screen.getByText('Alumnos')).toBeInTheDocument();
    expect(screen.getByText('Actividades')).toBeInTheDocument();
    expect(screen.getByText('Atrasados')).toBeInTheDocument();
    expect(screen.getByText('Equipo')).toBeInTheDocument();
    // Removed tabs: avisos, tareas, coloquios (now top-level routes)
    expect(screen.queryByText('Avisos')).not.toBeInTheDocument();
    expect(screen.queryByText('Mis Tareas')).not.toBeInTheDocument();
    expect(screen.queryByText('Mis Coloquios')).not.toBeInTheDocument();
    // Renamed: "Calificaciones" → "Actividades"
    expect(screen.queryByText('Calificaciones')).not.toBeInTheDocument();
  });
});
