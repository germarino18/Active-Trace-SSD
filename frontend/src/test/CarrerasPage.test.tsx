import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { CarrerasPage } from '@/features/admin/pages/CarrerasPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['ADMIN'], permissions: ['estructura:*'] } },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['ADMIN', 'estructura:*'].includes(p)),
  }),
}));

const mockCarreras = [
  { id: '1', codigo: 'ING', nombre: 'Ingeniería', activa: true },
  { id: '2', codigo: 'LIC', nombre: 'Licenciatura', activa: true },
  { id: '3', codigo: 'PROF', nombre: 'Profesorado', activa: false },
];

let mockCarrerasState: Record<string, unknown> = {
  data: { items: mockCarreras, total: 3 },
  isLoading: false,
  isError: false,
};

vi.mock('@/features/admin/hooks/useEstructura', () => ({
  useCarreras: () => mockCarrerasState,
  useCrearCarrera: () => ({ mutate: vi.fn(), isPending: false }),
  useActualizarCarrera: () => ({ mutate: vi.fn(), isPending: false }),
  useEliminarCarrera: () => ({ mutate: vi.fn(), isPending: false }),
  useToggleCarreraEstado: () => ({ mutate: vi.fn(), isPending: false }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <CarrerasPage />
    </TestWrapper>,
  );
}

describe('CarrerasPage', () => {
  afterEach(() => {
    mockCarrerasState = { data: { items: mockCarreras, total: 3 }, isLoading: false, isError: false };
  });

  it('renders page with title and total count', () => {
    renderPage();
    expect(screen.getByText(/3 carrera\(s\) registrada\(s\)/)).toBeInTheDocument();
    expect(screen.getByText('Nueva carrera')).toBeInTheDocument();
  });

  it('renders table with carreras data', () => {
    renderPage();
    expect(screen.getByText('Ingeniería')).toBeInTheDocument();
    expect(screen.getByText('Licenciatura')).toBeInTheDocument();
    expect(screen.getByText('Profesorado')).toBeInTheDocument();
    expect(screen.getByText('ING')).toBeInTheDocument();
  });

  it('renders active/inactive badges', () => {
    renderPage();
    expect(screen.getAllByText('Activa').length).toBe(2);
    expect(screen.getByText('Inactiva')).toBeInTheDocument();
  });

  it('renders action buttons for each row', () => {
    renderPage();
    expect(screen.getAllByTitle('Editar').length).toBe(3);
    expect(screen.getAllByTitle('Eliminar').length).toBe(3);
  });

  it('shows loading state', () => {
    mockCarrerasState = { data: undefined, isLoading: true, isError: false };
    renderPage();
    expect(screen.queryByText('Ingeniería')).not.toBeInTheDocument();
    expect(screen.queryByText('Nueva carrera')).toBeInTheDocument();
  });

  it('shows error state', () => {
    mockCarrerasState = { data: undefined, isLoading: false, isError: true };
    renderPage();
    expect(screen.getByText('Error al cargar carreras')).toBeInTheDocument();
  });

  it('shows empty state when no carreras', () => {
    mockCarrerasState = { data: { items: [], total: 0 }, isLoading: false, isError: false };
    renderPage();
    expect(screen.getByText('No hay carreras registradas')).toBeInTheDocument();
  });

  it('opens create modal on Nueva carrera click', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByText('Nueva carrera'));
    expect(screen.getByPlaceholderText('Ej: MAT-101')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ej: Matemática I')).toBeInTheDocument();
  });
});
