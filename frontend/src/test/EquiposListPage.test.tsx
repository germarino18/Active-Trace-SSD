import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { EquiposListPage } from '@/features/coordinacion/pages/EquiposListPage';

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

const mockAsignaciones = [
  {
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
  },
  {
    id: '2',
    docente: { id: 'd2', nombre: 'María', apellido: 'García', email: 'maria@test.com' },
    materia_id: 'm2',
    materia_nombre: 'Física',
    carrera_id: 'c1',
    carrera_nombre: 'Ingeniería',
    cohorte_id: 'co1',
    cohorte_nombre: '2024',
    rol: 'TUTOR' as const,
    vigencia_desde: '2024-02-01',
    vigencia_hasta: '2024-11-30',
    estado: 'Activa' as const,
    comisiones: ['B'],
    created_at: '2024-02-01',
    updated_at: '2024-02-01',
  },
  {
    id: '3',
    docente: { id: 'd3', nombre: 'Carlos', apellido: 'López', email: 'carlos@test.com' },
    materia_id: 'm3',
    materia_nombre: 'Química',
    carrera_id: 'c2',
    carrera_nombre: 'Licenciatura',
    cohorte_id: 'co2',
    cohorte_nombre: '2023',
    rol: 'NEXO' as const,
    vigencia_desde: '2023-03-01',
    vigencia_hasta: '2023-12-31',
    estado: 'Vencida' as const,
    comisiones: ['A', 'B'],
    created_at: '2023-03-01',
    updated_at: '2023-03-01',
  },
];

vi.mock('@/features/coordinacion/hooks/useEquipos', () => ({
  useEquipos: () => ({
    data: { asignaciones: mockAsignaciones, total: 3 },
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
  useClonarEquipo: () => ({
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
      <EquiposListPage />
    </TestWrapper>,
  );
}

describe('EquiposListPage', () => {
  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Equipos Docentes')).toBeInTheDocument();
    expect(screen.getByText('Gestioná las asignaciones del cuerpo docente')).toBeInTheDocument();
  });

  it('renders filter elements', () => {
    renderPage();
    expect(screen.getByPlaceholderText('Buscar materia...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Buscar carrera...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ej: 2024')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Nombre o email...')).toBeInTheDocument();
  });

  it('renders action buttons for COORDINADOR', () => {
    renderPage();
    expect(screen.getByText('Nueva asignación')).toBeInTheDocument();
    expect(screen.getByText('Asignación masiva')).toBeInTheDocument();
    expect(screen.getByText('Clonar equipo')).toBeInTheDocument();
    expect(screen.getByText('Modificar vigencia')).toBeInTheDocument();
    expect(screen.getByText('Exportar')).toBeInTheDocument();
  });

  it('renders table with assignment data', () => {
    renderPage();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Física')).toBeInTheDocument();
    expect(screen.getByText('Química')).toBeInTheDocument();
    expect(screen.getByText('Pérez, Juan')).toBeInTheDocument();
    expect(screen.getByText('García, María')).toBeInTheDocument();
    expect(screen.getByText('López, Carlos')).toBeInTheDocument();
  });

  it('shows manage action buttons (edit/delete) for COORDINADOR', () => {
    renderPage();
    const editButtons = screen.getAllByTitle('Editar');
    const deleteButtons = screen.getAllByTitle('Eliminar');
    expect(editButtons.length).toBe(3);
    expect(deleteButtons.length).toBe(3);
  });
});
