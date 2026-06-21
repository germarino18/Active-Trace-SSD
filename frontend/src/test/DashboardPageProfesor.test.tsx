/**
 * DashboardPage — generic static tests.
 *
 * After the D4 split (fix-profesor-dictados-ux-round2), DashboardPage no longer calls
 * useProfesorDashboard. Professor live metrics moved to ProfesorMetricsDashboardPage.
 * These tests verify the reverted generic-static behavior.
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

// Mock auth hook
vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// DashboardPage no longer imports useProfesorDashboard — no need to mock it here.
// If any import attempt sneaks in, this catch-all mock prevents a real HTTP call.
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

describe('DashboardPage — generic static (post-D4 split)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders "Panel Principal" heading for PROFESOR role', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('PROFESOR') as ReturnType<typeof useAuth>);
    renderPage();
    expect(screen.getByRole('heading', { name: /panel principal/i })).toBeInTheDocument();
  });

  it('renders static ROLE_CONFIG stat labels for PROFESOR (no live values)', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('PROFESOR') as ReturnType<typeof useAuth>);
    renderPage();
    // Static labels from ROLE_CONFIG.PROFESOR
    expect(screen.getByText('Materias asignadas')).toBeInTheDocument();
    expect(screen.getByText('Alumnos en riesgo')).toBeInTheDocument();
    expect(screen.getByText('Entregas pendientes')).toBeInTheDocument();
    // All values are static '—' (no live fetch)
    expect(screen.getAllByText('—').length).toBeGreaterThan(0);
  });

  it('does NOT call useProfesorDashboard for PROFESOR role (live metrics moved to /profesor-dashboard)', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('PROFESOR') as ReturnType<typeof useAuth>);
    renderPage();
    expect(mockUseProfesorDashboard).not.toHaveBeenCalled();
  });

  it('does NOT call useProfesorDashboard for ALUMNO role', () => {
    mockUseAuth.mockReturnValue(makeAuthSession('ALUMNO') as ReturnType<typeof useAuth>);
    renderPage();
    expect(mockUseProfesorDashboard).not.toHaveBeenCalled();
  });
});
