import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

// Mock the hook module directly (matches MonitorSeguimientoPage pattern)
vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useActividadesDictado: vi.fn(),
  useCalificacionesDictado: vi.fn(),
  useMutationEditarCalificacion: vi.fn(),
  useMutationCrearActividad: vi.fn(),
  useMutationEliminarActividad: vi.fn(),
  useMutationSubirCalificacionesCsv: vi.fn(),
  useAtrasadosProfesor: vi.fn(),
  useMutationComunicadoAtrasadoNull: vi.fn(),
  useMutationComunicadoAtrasados: vi.fn(),
  useEquipoDictado: vi.fn(),
  useAvisosMios: vi.fn(),
  useMutationCrearAviso: vi.fn(),
  useColoquiosMios: vi.fn(),
  useAlumnosDisponibles: vi.fn(),
}));

import { useProfesorDashboard } from '@/features/profesor/hooks/useProfesor';
import { ProfesorDashboardListPage } from '@/features/profesor/pages/ProfesorDashboardListPage';

const mockUseProfesorDashboard = vi.mocked(useProfesorDashboard);

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ProfesorDashboardListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ProfesorDashboardListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page title', () => {
    mockUseProfesorDashboard.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    expect(screen.getByText('Mis Dictados')).toBeInTheDocument();
  });

  it('shows loading state while fetching', () => {
    mockUseProfesorDashboard.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    // LoadingState renders table skeleton rows — the page should not show content
    expect(screen.queryByText('Mis Dictados')).toBeInTheDocument();
    // No dictado rows visible during loading
    expect(screen.queryByText('Ver dictado')).not.toBeInTheDocument();
  });

  it('renders empty state when no dictados', () => {
    mockUseProfesorDashboard.mockReturnValue({
      data: { materias_asignadas: [], total_alumnos: 0, total_encuentros: 0, total_atrasados: 0 },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    expect(screen.getByText('No tenés dictados asignados')).toBeInTheDocument();
  });

  it('renders dictado list with links when data is present', () => {
    mockUseProfesorDashboard.mockReturnValue({
      data: {
        materias_asignadas: [
          { dictado_id: 'd1', materia_id: 'm1', materia_nombre: 'Matemática', n_alumnos: 20 },
          { dictado_id: 'd2', materia_id: 'm2', materia_nombre: 'Lengua', n_alumnos: 15 },
        ],
        total_alumnos: 35,
        total_encuentros: 5,
        total_atrasados: 3,
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Lengua')).toBeInTheDocument();
    expect(screen.getAllByText('Ver dictado')).toHaveLength(2);
  });
});
