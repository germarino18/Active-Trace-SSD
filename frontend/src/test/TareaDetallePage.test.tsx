import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TareaDetallePage } from '@/features/coordinacion/pages/TareaDetallePage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const mockCambiarEstado = { mutateAsync: vi.fn(), isPending: false };
const mockAgregarComentario = { mutateAsync: vi.fn() };
const mockDelegarTarea = { mutateAsync: vi.fn(), isPending: false };

const mockTarea = {
  id: 't1',
  tenant_id: 't1',
  titulo: 'Corregir parciales',
  descripcion: 'Corregir los parciales de la materia Matemática',
  asignado_id: 'u1',
  asignado_nombre: 'Juan Pérez',
  asignado_por_id: 'admin',
  asignado_por_nombre: 'Admin',
  materia_id: 'm1',
  materia_nombre: 'Matemática',
  cohorte_id: 'co1',
  estado: 'Pendiente' as const,
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-15T10:00:00Z',
  comentarios: [
    {
      id: 'c1',
      tarea_id: 't1',
      autor_id: 'u1',
      autor_nombre: 'Juan Pérez',
      contenido: 'Empecé con la corrección',
      created_at: '2024-01-16T10:00:00Z',
    },
    {
      id: 'c2',
      tarea_id: 't1',
      autor_id: 'admin',
      autor_nombre: 'Admin',
      contenido: 'Recordá que hay fecha límite',
      created_at: '2024-01-17T10:00:00Z',
    },
  ],
};

vi.mock('@/features/coordinacion/hooks/useTareas', () => ({
  useTarea: (id: string | undefined) => ({
    data: id === 't1' ? mockTarea : null,
    isLoading: false,
  }),
  useCambiarEstado: () => mockCambiarEstado,
  useAgregarComentario: () => mockAgregarComentario,
  useDelegarTarea: () => mockDelegarTarea,
  useTareas: () => ({
    data: { items: [], total: 0 },
    isLoading: false,
  }),
  useMisTareas: () => ({
    data: { items: [], total: 0 },
    isLoading: false,
  }),
  useCrearTarea: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

function renderPage(tareaId = 't1') {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/tareas/${tareaId}`]}>
        <Routes>
          <Route path="/tareas/:id" element={<TareaDetallePage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('TareaDetallePage', () => {
  it('renders tarea title and badge', () => {
    renderPage();
    expect(screen.getByText('Corregir parciales')).toBeInTheDocument();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('renders tarea details', () => {
    renderPage();
    expect(screen.getAllByText('Juan Pérez').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Admin').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Matemática')).toBeInTheDocument();
  });

  it('renders description', () => {
    renderPage();
    expect(
      screen.getByText('Corregir los parciales de la materia Matemática'),
    ).toBeInTheDocument();
  });

  it('shows state transition buttons for Pendiente estado', () => {
    renderPage();
    expect(screen.getByText('Iniciar')).toBeInTheDocument();
    expect(screen.getByText('Cancelar')).toBeInTheDocument();
  });

  it('renders comment thread', () => {
    renderPage();
    expect(screen.getByText('Comentarios')).toBeInTheDocument();
    expect(screen.getByText('Empecé con la corrección')).toBeInTheDocument();
    expect(screen.getByText('Recordá que hay fecha límite')).toBeInTheDocument();
  });

  it('shows delegar button for non-terminal estados', () => {
    renderPage();
    expect(screen.getByText('Delegar')).toBeInTheDocument();
  });

  it('calls cambiarEstado when Iniciar is clicked', async () => {
    const user = userEvent.setup();
    mockCambiarEstado.mutateAsync.mockResolvedValueOnce(mockTarea);

    renderPage();
    await user.click(screen.getByText('Iniciar'));

    await waitFor(() => {
      expect(mockCambiarEstado.mutateAsync).toHaveBeenCalledWith({
        tareaId: 't1',
        estado: 'En progreso',
      });
    });
  });

  it('shows cancel reason input when Cancelar is clicked', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByText('Cancelar'));

    expect(screen.getByPlaceholderText('Explicá el motivo...')).toBeInTheDocument();
    expect(screen.getByText('Confirmar cancelación')).toBeInTheDocument();
  });

  it('shows error message when tarea is not found', () => {
    renderPage('nonexistent');
    expect(screen.getByText('Tarea no encontrada.')).toBeInTheDocument();
  });
});
