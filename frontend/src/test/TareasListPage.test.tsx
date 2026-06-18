import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TareasListPage } from '@/features/coordinacion/pages/TareasListPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['COORDINADOR'],
        permissions: ['coordinacion:tareas:crear'],
      },
    },
    hasPermission: (perm: string) => perm === 'coordinacion:tareas:crear',
    hasAnyPermission: () => false,
  }),
}));

vi.mock('@/features/coordinacion/hooks/useTareas', () => ({
  useTareas: () => ({
    data: {
      items: [
        {
          id: 't1',
          tenant_id: 't1',
          titulo: 'Corregir parciales',
          descripcion: 'Corregir parciales de matemática',
          asignado_id: 'u1',
          asignado_nombre: 'Juan Pérez',
          asignado_por_id: 'admin',
          asignado_por_nombre: 'Admin',
          materia_id: 'm1',
          materia_nombre: 'Matemática',
          estado: 'Pendiente' as const,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          comentarios: [],
        },
        {
          id: 't2',
          tenant_id: 't1',
          titulo: 'Preparar examen',
          descripcion: 'Preparar examen final',
          asignado_id: 'u2',
          asignado_nombre: 'María García',
          asignado_por_id: 'admin',
          asignado_por_nombre: 'Admin',
          materia_id: 'm2',
          materia_nombre: 'Física',
          estado: 'En progreso' as const,
          created_at: '2024-02-01T10:00:00Z',
          updated_at: '2024-02-01T10:00:00Z',
          comentarios: [],
        },
        {
          id: 't3',
          tenant_id: 't1',
          titulo: 'Actualizar programa',
          descripcion: 'Actualizar programa 2024',
          asignado_id: 'u3',
          asignado_nombre: 'Carlos López',
          asignado_por_id: 'admin',
          asignado_por_nombre: 'Admin',
          materia_id: undefined,
          materia_nombre: undefined,
          estado: 'Resuelta' as const,
          created_at: '2024-03-01T10:00:00Z',
          updated_at: '2024-03-01T10:00:00Z',
          comentarios: [],
        },
      ],
      total: 3,
    },
    isLoading: false,
    isError: false,
  }),
  useMisTareas: () => ({
    data: { items: [], total: 0 },
    isLoading: false,
  }),
  useTarea: () => ({
    data: null,
    isLoading: false,
  }),
  useCambiarEstado: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useAgregarComentario: () => ({
    mutateAsync: vi.fn(),
  }),
  useDelegarTarea: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useCrearTarea: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <TareasListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('TareasListPage', () => {
  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Tareas')).toBeInTheDocument();
    expect(screen.getByText('Administración global de tareas.')).toBeInTheDocument();
  });

  it('renders filter elements', () => {
    renderPage();
    expect(screen.getByPlaceholderText('Título o descripción')).toBeInTheDocument();
    expect(screen.getAllByPlaceholderText('ID del usuario').length).toBe(2);
    expect(screen.getByPlaceholderText('ID de la materia')).toBeInTheDocument();
  });

  it('renders tareas data in table', () => {
    renderPage();
    expect(screen.getByText('Corregir parciales')).toBeInTheDocument();
    expect(screen.getByText('Preparar examen')).toBeInTheDocument();
    expect(screen.getByText('Actualizar programa')).toBeInTheDocument();
  });

  it('renders state badges', () => {
    renderPage();
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('En progreso').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Resuelta').length).toBeGreaterThanOrEqual(1);
  });

  it('renders assigned users', () => {
    renderPage();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('María García')).toBeInTheDocument();
    expect(screen.getByText('Carlos López')).toBeInTheDocument();
  });

  it('shows create button when user has permission', () => {
    renderPage();
    expect(screen.getByText('Nueva Tarea')).toBeInTheDocument();
  });
});
