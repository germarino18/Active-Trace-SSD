import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { ClonarEquipoPage } from '@/features/coordinacion/pages/ClonarEquipoPage';

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

vi.mock('@/features/coordinacion/hooks/useEquipos', () => ({
  useClonarEquipo: () => ({
    mutateAsync: mockMutateAsync,
    isPending: false,
  }),
  useEquipos: () => ({
    data: { asignaciones: [], total: 0 },
    isLoading: false,
  }),
  useDocentes: () => ({
    data: [],
    isLoading: false,
  }),
  useAsignacionMasiva: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
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
  useModificarVigencia: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <ClonarEquipoPage />
    </TestWrapper>,
  );
}

describe('ClonarEquipoPage', () => {
  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Clonar Equipo Docente')).toBeInTheDocument();
    expect(
      screen.getByText('Copiá todas las asignaciones de un equipo origen a un destino'),
    ).toBeInTheDocument();
  });

  it('renders source and destination sections', () => {
    renderPage();
    expect(screen.getByText('Equipo origen')).toBeInTheDocument();
    expect(screen.getByText('Equipo destino')).toBeInTheDocument();
  });

  it('renders all input fields', () => {
    renderPage();
    const inputs = screen.getAllByPlaceholderText(/^ID de (materia|carrera)$/);
    const cohorteInputs = screen.getAllByPlaceholderText(/^Ej: /);
    expect(inputs.length).toBe(4);
    expect(cohorteInputs.length).toBe(2);
  });

  it('shows success modal after successful clone with asignaciones', async () => {
    const user = userEvent.setup();
    mockMutateAsync.mockResolvedValueOnce({ clonadas: 5 });

    renderPage();
    const materiaInputs = screen.getAllByPlaceholderText('ID de materia');
    const carreraInputs = screen.getAllByPlaceholderText('ID de carrera');

    await user.type(materiaInputs[0]!, 'm1');
    await user.type(carreraInputs[0]!, 'c1');
    await user.type(screen.getAllByPlaceholderText('ID de materia')[1]!, 'm2');
    await user.type(screen.getAllByPlaceholderText('ID de carrera')[1]!, 'c2');
    await user.type(screen.getAllByPlaceholderText(/^Ej: /)[0]!, '2024');
    await user.type(screen.getAllByPlaceholderText(/^Ej: /)[1]!, '2025');

    await user.click(screen.getByText('Clonar equipo'));

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalledWith({
        origen_materia_id: 'm1',
        origen_carrera_id: 'c1',
        origen_cohorte_id: '2024',
        destino_materia_id: 'm2',
        destino_carrera_id: 'c2',
        destino_cohorte_id: '2025',
      });
    });

    await waitFor(() => {
      expect(screen.getByText('5 asignaciones copiadas al equipo destino')).toBeInTheDocument();
      expect(screen.getByText('Equipo clonado')).toBeInTheDocument();
    });
  });

  it('shows empty state message when 0 asignaciones clonadas', async () => {
    const user = userEvent.setup();
    mockMutateAsync.mockResolvedValueOnce({ clonadas: 0 });

    renderPage();
    const materiaInputs = screen.getAllByPlaceholderText('ID de materia');

    await user.type(materiaInputs[0]!, 'm1');
    await user.type(screen.getAllByPlaceholderText('ID de materia')[1]!, 'm2');
    await user.type(screen.getAllByPlaceholderText('ID de carrera')[0]!, 'c1');
    await user.type(screen.getAllByPlaceholderText('ID de carrera')[1]!, 'c2');
    await user.type(screen.getAllByPlaceholderText(/^Ej: /)[0]!, '2024');
    await user.type(screen.getAllByPlaceholderText(/^Ej: /)[1]!, '2025');

    await user.click(screen.getByText('Clonar equipo'));

    await waitFor(() => {
      expect(
        screen.getByText('No se clonaron asignaciones. El equipo origen puede estar vacío.'),
      ).toBeInTheDocument();
    });
  });
});
