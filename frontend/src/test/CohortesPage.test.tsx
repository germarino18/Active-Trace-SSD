import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { CohortesPage } from '@/features/admin/pages/CohortesPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['ADMIN'], permissions: ['estructura:*'] } },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['ADMIN', 'estructura:*'].includes(p)),
  }),
}));

const mockCohortes = [
  { id: '1', nombre: 'Cohorte 2024', anio: 2024, vig_desde: '2024-03-01', vig_hasta: '2024-12-31', estado: 'Activa', carrera_id: 'c1' },
  { id: '2', nombre: 'Cohorte 2023', anio: 2023, vig_desde: '2023-03-01', vig_hasta: null, estado: 'Inactiva', carrera_id: 'c2' },
];

let mockCohortesState: Record<string, unknown> = {
  data: { items: mockCohortes, total: 2 },
  isLoading: false,
  isError: false,
};

vi.mock('@/features/admin/hooks/useEstructura', () => ({
  useCohortes: () => mockCohortesState,
  useCarreras: () => ({ data: { items: [{ id: 'c1', codigo: 'ING', nombre: 'Ingeniería' }], total: 1 }, isLoading: false }),
  useCrearCohorte: () => ({ mutate: vi.fn(), isPending: false, mutateAsync: vi.fn() }),
  useActualizarCohorte: () => ({ mutate: vi.fn(), isPending: false, mutateAsync: vi.fn() }),
  useEliminarCohorte: () => ({ mutate: vi.fn(), isPending: false }),
  useToggleCohorteEstado: () => ({ mutate: vi.fn(), isPending: false }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <CohortesPage />
    </TestWrapper>,
  );
}

describe('CohortesPage', () => {
  afterEach(() => {
    mockCohortesState = { data: { items: mockCohortes, total: 2 }, isLoading: false, isError: false };
  });

  it('renders page with title and total count', () => {
    renderPage();
    expect(screen.getByText(/2 cohorte\(s\) registrado\(s\)/)).toBeInTheDocument();
    expect(screen.getByText('Nuevo cohorte')).toBeInTheDocument();
  });

  it('renders table with cohortes data', () => {
    renderPage();
    expect(screen.getByText('Cohorte 2024')).toBeInTheDocument();
    expect(screen.getByText('Cohorte 2023')).toBeInTheDocument();
    expect(screen.getByText('2024')).toBeInTheDocument();
    expect(screen.getByText('2023')).toBeInTheDocument();
  });

  it('renders active/inactive badges', () => {
    renderPage();
    expect(screen.getByText('Activa')).toBeInTheDocument();
    expect(screen.getByText('Inactiva')).toBeInTheDocument();
  });

  it('renders action buttons for each row', () => {
    renderPage();
    expect(screen.getAllByTitle('Editar').length).toBe(2);
    expect(screen.getAllByTitle('Eliminar').length).toBe(2);
  });

  it('shows loading state', () => {
    mockCohortesState = { data: undefined, isLoading: true, isError: false };
    renderPage();
    expect(screen.queryByText('Cohorte 2024')).not.toBeInTheDocument();
  });

  it('shows error state', () => {
    mockCohortesState = { data: undefined, isLoading: false, isError: true };
    renderPage();
    expect(screen.getByText('Error al cargar cohortes')).toBeInTheDocument();
  });

  it('shows empty state when no cohortes', () => {
    mockCohortesState = { data: { items: [], total: 0 }, isLoading: false, isError: false };
    renderPage();
    expect(screen.getByText('No hay cohortes registrados')).toBeInTheDocument();
  });

  it('opens create modal on Nuevo cohorte click', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByText('Nuevo cohorte'));
    expect(screen.getByPlaceholderText('Ej: Cohorte 2024')).toBeInTheDocument();
  });
});
