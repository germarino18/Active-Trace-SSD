import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { MateriasPage } from '@/features/admin/pages/MateriasPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['ADMIN'], permissions: ['estructura:*'] } },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['ADMIN', 'estructura:*'].includes(p)),
  }),
}));

const mockMaterias = [
  { id: '1', nombre: 'Álgebra', codigo: 'ALG-101', carrera_id: 'c1', carrera_nombre: 'Ingeniería', cohorte_id: 'co1', cohorte_nombre: '2024', activa: true },
  { id: '2', nombre: 'Física', codigo: 'FIS-101', activa: true },
];

const mockCarreras = [
  { id: 'c1', codigo: 'ING', nombre: 'Ingeniería', activa: true },
];

const mockCohortes = [
  { id: 'co1', nombre: '2024', anio_inicio: 2024, vigencia_desde: '2024-03-01', activa: true },
];

let mockMateriasState: Record<string, unknown> = {
  data: { items: mockMaterias, total: 2 },
  isLoading: false,
  isError: false,
};

vi.mock('@/features/admin/hooks/useEstructura', () => ({
  useMaterias: () => mockMateriasState,
  useCarreras: () => ({ data: { items: mockCarreras, total: 1 }, isLoading: false }),
  useCohortes: () => ({ data: { items: mockCohortes, total: 1 }, isLoading: false }),
  useCrearMateria: () => ({ mutate: vi.fn(), isPending: false }),
  useActualizarMateria: () => ({ mutate: vi.fn(), isPending: false }),
  useToggleMateriaEstado: () => ({ mutate: vi.fn(), isPending: false }),
  useSubirPrograma: () => ({ mutate: vi.fn(), isPending: false, isSuccess: false }),
  useEvaluaciones: () => ({ data: { items: [], total: 0 }, isLoading: false }),
  useCrearEvaluacion: () => ({ mutate: vi.fn(), isPending: false }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <MateriasPage />
    </TestWrapper>,
  );
}

describe('MateriasPage', () => {
  afterEach(() => {
    mockMateriasState = { data: { items: mockMaterias, total: 2 }, isLoading: false, isError: false };
  });

  it('renders page with title and total count', () => {
    renderPage();
    expect(screen.getByText(/2 materia\(s\) registrada\(s\)/)).toBeInTheDocument();
    expect(screen.getByText('Nueva materia')).toBeInTheDocument();
  });

  it('renders table with materias data', () => {
    renderPage();
    expect(screen.getByText('Álgebra')).toBeInTheDocument();
    expect(screen.getByText('Física')).toBeInTheDocument();
    expect(screen.getByText('ALG-101')).toBeInTheDocument();
    expect(screen.getByText('Ingeniería')).toBeInTheDocument();
    expect(screen.getByText('2024')).toBeInTheDocument();
  });

  it('renders active/inactive badges', () => {
    renderPage();
    expect(screen.getAllByText('Activa').length).toBe(2);
  });

  it('renders action buttons for each row', () => {
    renderPage();
    expect(screen.getAllByTitle('Editar').length).toBe(2);
  });

  it('shows loading state', () => {
    mockMateriasState = { data: undefined, isLoading: true, isError: false };
    renderPage();
    expect(screen.queryByText('Álgebra')).not.toBeInTheDocument();
  });

  it('shows error state', () => {
    mockMateriasState = { data: undefined, isLoading: false, isError: true };
    renderPage();
    expect(screen.getByText('Error al cargar materias')).toBeInTheDocument();
  });

  it('shows empty state when no materias', () => {
    mockMateriasState = { data: { items: [], total: 0 }, isLoading: false, isError: false };
    renderPage();
    expect(screen.getByText('No hay materias registradas')).toBeInTheDocument();
  });

  it('opens create modal on Nueva materia click', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByText('Nueva materia'));
    expect(screen.getByPlaceholderText('Ej: Álgebra')).toBeInTheDocument();
  });
});
