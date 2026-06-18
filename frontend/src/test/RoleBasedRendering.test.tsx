import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EquiposListPage } from '@/features/coordinacion/pages/EquiposListPage';
import { MisEquiposPage } from '@/features/coordinacion/pages/MisEquiposPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

let mockUserRoles: string[] = [];
let mockUserPermissions: string[] = [];

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: mockUserRoles,
        permissions: mockUserPermissions,
      },
    },
    hasPermission: (perm: string) => mockUserPermissions.includes(perm),
    hasAnyPermission: (perms: string[]) => perms.some((p) =>
      [...mockUserRoles, ...mockUserPermissions].includes(p),
    ),
  }),
}));

const mockAsignacion = {
  id: '1',
  docente: { id: 'd1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com' },
  materia_id: 'm1',
  materia_nombre: 'Matemática',
  carrera_id: 'c1',
  carrera_nombre: 'Ingeniería',
  cohorte_id: 'co1',
  cohorte_nombre: '2024',
  rol: 'PROFESOR' as const,
  vigencia_desde: '2024-01-01',
  vigencia_hasta: '2024-12-31',
  estado: 'Activa' as const,
  comisiones: ['A'],
  created_at: '2024-01-01',
  updated_at: '2024-01-01',
};

vi.mock('@/features/coordinacion/hooks/useEquipos', () => ({
  useEquipos: () => ({
    data: { asignaciones: [mockAsignacion], total: 1 },
    isLoading: false,
  }),
  useMisEquipos: () => ({
    data: { asignaciones: [mockAsignacion], total: 1 },
    isLoading: false,
    error: null,
  }),
  useEliminarAsignacion: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
  useDocentes: () => ({
    data: [],
    isLoading: false,
  }),
  useAsignacionMasiva: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useClonarEquipo: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useCrearAsignacion: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
  useActualizarAsignacion: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
  useModificarVigencia: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
}));

function renderWithProviders(ui: React.ReactElement) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('RoleBasedRendering - PROFESOR', () => {
  beforeEach(() => {
    mockUserRoles = ['PROFESOR'];
    mockUserPermissions = ['PROFESOR'];
  });

  it('shows MisEquiposPage with data for PROFESOR', () => {
    renderWithProviders(<MisEquiposPage />);
    expect(screen.getByText('Mis Equipos')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
  });

  it('shows EquiposListPage for PROFESOR but without manage buttons', () => {
    renderWithProviders(<EquiposListPage />);
    expect(screen.getByText('Equipos Docentes')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();

    expect(screen.queryByText('Nueva asignación')).not.toBeInTheDocument();
    expect(screen.queryByText('Asignación masiva')).not.toBeInTheDocument();
    expect(screen.queryByText('Clonar equipo')).not.toBeInTheDocument();
    expect(screen.queryByText('Modificar vigencia')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Editar')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Eliminar')).not.toBeInTheDocument();
  });
});

describe('RoleBasedRendering - COORDINADOR', () => {
  beforeEach(() => {
    mockUserRoles = ['COORDINADOR'];
    mockUserPermissions = ['COORDINADOR', 'equipos:*'];
  });

  it('shows EquiposListPage with manage buttons for COORDINADOR', () => {
    renderWithProviders(<EquiposListPage />);
    expect(screen.getByText('Nueva asignación')).toBeInTheDocument();
    expect(screen.getByText('Asignación masiva')).toBeInTheDocument();
    expect(screen.getByText('Clonar equipo')).toBeInTheDocument();
    expect(screen.getByText('Modificar vigencia')).toBeInTheDocument();
    expect(screen.getByTitle('Editar')).toBeInTheDocument();
    expect(screen.getByTitle('Eliminar')).toBeInTheDocument();
  });
});
