import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

// Mock auth hook
vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// Mock profesor dashboard hook
vi.mock('@/features/profesor/hooks/useProfesor', () => ({
  useProfesorDashboard: vi.fn(),
  useDictadoMetricas: vi.fn(),
  usePadronDictado: vi.fn(),
  useMutationAgregarAlumno: vi.fn(),
  useMutationQuitarAlumno: vi.fn(),
  useActividadesDictado: vi.fn(),
  useCalificacionesDictado: vi.fn(),
  useMutationEditarCalificacion: vi.fn(),
  useAtrasadosProfesor: vi.fn(),
  useMutationComunicadoAtrasadoNull: vi.fn(),
  useEquipoDictado: vi.fn(),
  useAvisosMios: vi.fn(),
  useColoquiosMios: vi.fn(),
}));

import { useAuth } from '@/features/auth/hooks/useAuth';
import { useProfesorDashboard } from '@/features/profesor/hooks/useProfesor';
import { DashboardPage } from '@/pages/DashboardPage';

const mockUseAuth = vi.mocked(useAuth);
const mockUseProfesorDashboard = vi.mocked(useProfesorDashboard);

function makeAuthSession(role: string) {
  return {
    session: {
      status: 'authenticated',
      user: {
        id: 'u1',
        nombre: 'Test',
        apellido: 'User',
        roles: [role],
        permissions: [],
        tenant_id: 't1',
      },
    },
    hasPermission: vi.fn(),
  };
}

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('DashboardPage — PROFESOR role', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders real stats labels from profesor dashboard when role is PROFESOR', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('PROFESOR') as ReturnType<typeof useAuth>);
    mockUseProfesorDashboard.mockReturnValue({
      data: {
        materias_asignadas: [
          { dictado_id: 'd1', materia_id: 'm1', materia_nombre: 'Álgebra', n_alumnos: 20 },
          { dictado_id: 'd2', materia_id: 'm2', materia_nombre: 'Análisis', n_alumnos: 18 },
        ],
        total_alumnos: 38,
        total_encuentros: 3,
        total_atrasados: 7,
      },
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    expect(screen.getByText('Materias asignadas')).toBeInTheDocument();
    // Value comes from materias_asignadas.length = 2
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('Alumnos en riesgo')).toBeInTheDocument();
    // total_atrasados = 7
    expect(screen.getByText('7')).toBeInTheDocument();
  });

  it('shows dash placeholder when profesor data not yet loaded', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('PROFESOR') as ReturnType<typeof useAuth>);
    mockUseProfesorDashboard.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    // StatCards should render with '—' placeholders
    expect(screen.getAllByText('—').length).toBeGreaterThan(0);
  });

  it('calls useProfesorDashboard with enabled=true when role is PROFESOR', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('PROFESOR') as ReturnType<typeof useAuth>);
    mockUseProfesorDashboard.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    expect(mockUseProfesorDashboard).toHaveBeenCalledWith(true);
  });

  it('calls useProfesorDashboard with enabled=false when role is ALUMNO', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('ALUMNO') as ReturnType<typeof useAuth>);
    mockUseProfesorDashboard.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof useProfesorDashboard>);

    renderPage();
    expect(mockUseProfesorDashboard).toHaveBeenCalledWith(false);
  });
});
