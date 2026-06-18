import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { AsignacionMasivaPage } from '@/features/coordinacion/pages/AsignacionMasivaPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['COORDINADOR'],
        permissions: ['COORDINADOR', 'equipos:*'],
      },
    },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['COORDINADOR', 'ADMIN'].includes(p)),
  }),
}));

const mockMutateAsync = vi.fn();
const mockDocentes = vi.hoisted(() => [
  { id: 'd1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com' },
  { id: 'd2', nombre: 'María', apellido: 'García', email: 'maria@test.com' },
  { id: 'd3', nombre: 'Carlos', apellido: 'López', email: 'carlos@test.com' },
]);

vi.mock('@/features/coordinacion/hooks/useEquipos', () => ({
  useDocentes: () => ({
    data: mockDocentes,
    isLoading: false,
  }),
  useAsignacionMasiva: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  }),
  useEquipos: () => ({
    data: { asignaciones: [], total: 0 },
    isLoading: false,
  }),
  useEliminarAsignacion: () => ({
    mutate: vi.fn(),
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
  useMisEquipos: () => ({
    data: { asignaciones: [], total: 0 },
    isLoading: false,
  }),
  useClonarEquipo: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useModificarVigencia: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <AsignacionMasivaPage />
    </TestWrapper>,
  );
}

describe('AsignacionMasivaPage', () => {
  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Asignación Masiva')).toBeInTheDocument();
    expect(
      screen.getByText('Asigná múltiples docentes a una misma materia en una sola operación'),
    ).toBeInTheDocument();
  });

  it('renders form with all required fields', () => {
    renderPage();
    expect(screen.getByPlaceholderText('ID de la materia')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('ID de la carrera')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('ID de la cohorte')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('renders teacher list with checkboxes', () => {
    renderPage();
    expect(screen.getByText('Pérez, Juan')).toBeInTheDocument();
    expect(screen.getByText('García, María')).toBeInTheDocument();
    expect(screen.getByText('López, Carlos')).toBeInTheDocument();
    expect(screen.getByText('juan@test.com')).toBeInTheDocument();
  });

  it('shows selected count', () => {
    renderPage();
    expect(screen.getByText('Docentes (0 seleccionados)')).toBeInTheDocument();
  });

  it('allows selecting and deselecting teachers', async () => {
    const user = userEvent.setup();
    renderPage();

    const checkboxes = screen.getAllByRole('checkbox');
    expect(checkboxes.length).toBe(3);

    await user.click(checkboxes[0]!);
    expect(screen.getByText('Docentes (1 seleccionados)')).toBeInTheDocument();

    await user.click(checkboxes[0]!);
    expect(screen.getByText('Docentes (0 seleccionados)')).toBeInTheDocument();
  });

  it('allows select all / deselect all', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByText('Seleccionar todos'));
    expect(screen.getByText('Docentes (3 seleccionados)')).toBeInTheDocument();

    await user.click(screen.getByText('Deseleccionar todos'));
    expect(screen.getByText('Docentes (0 seleccionados)')).toBeInTheDocument();
  });

  it('submits form and shows success modal', async () => {
    const user = userEvent.setup();
    mockMutateAsync.mockResolvedValueOnce({ creadas: 3, omitidas: 0 });

    const { container } = renderPage();

    await user.type(screen.getByPlaceholderText('ID de la materia'), 'm1');
    await user.type(screen.getByPlaceholderText('ID de la carrera'), 'c1');
    await user.type(screen.getByPlaceholderText('ID de la cohorte'), 'co1');

    const rolSelect = screen.getAllByRole('combobox')[0]!;
    await user.selectOptions(rolSelect, 'PROFESOR');

    const dateInputs = container.querySelectorAll<HTMLInputElement>('input[type="date"]');
    await user.type(dateInputs[0]!, '2024-01-01');
    await user.type(dateInputs[1]!, '2024-12-31');

    const checkboxes = screen.getAllByRole('checkbox');
    await user.click(checkboxes[0]!);
    await user.click(checkboxes[1]!);

    const submitButton = screen.getByText('Asignar (2 docentes)');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        usuario_ids: ['d1', 'd2'],
        materia_id: 'm1',
        carrera_id: 'c1',
        cohorte_id: 'co1',
        rol: 'PROFESOR',
        vigencia_desde: '2024-01-01',
        vigencia_hasta: '2024-12-31',
      });
    });

    await waitFor(() => {
      expect(screen.getByText('3 asignaciones creadas correctamente')).toBeInTheDocument();
    });
  });
});
