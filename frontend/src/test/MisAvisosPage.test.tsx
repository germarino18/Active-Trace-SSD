import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

let mockQueryData: unknown = null;
let mockIsLoading = false;
let mockError: Error | null = null;
let mockMutateIsPending = false;
const mockRefetch = vi.fn();
const mockMutate = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: () => ({
      data: mockQueryData,
      isLoading: mockIsLoading,
      error: mockError,
      refetch: mockRefetch,
    }),
    useMutation: () => ({
      mutate: mockMutate,
      isPending: mockMutateIsPending,
      isError: false,
      isSuccess: false,
    }),
  };
});

import { MisAvisosPage } from '@/features/alumno/pages/MisAvisosPage';

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisAvisosPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MisAvisosPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
    mockMutateIsPending = false;
  });

  it('renders avisos with prioridades and confirm button for require_ack', () => {
    mockQueryData = [
      {
        id: 'a1', titulo: 'Recordatorio parcial', contenido: 'El parcial se acerca',
        prioridad: 2, fecha_publicacion: '2025-06-01', require_ack: false, leido: true, vigencia_hasta: null,
      },
      {
        id: 'a2', titulo: 'Urgente: cambio de fecha', contenido: 'Se cambió la fecha del final',
        prioridad: 1, fecha_publicacion: '2025-06-10', require_ack: true, leido: false, vigencia_hasta: '2025-06-20',
      },
    ];
    renderPage();

    expect(screen.getByText('Avisos')).toBeInTheDocument();
    expect(screen.getByText('Recordatorio parcial')).toBeInTheDocument();
    expect(screen.getByText('Urgente: cambio de fecha')).toBeInTheDocument();
    expect(screen.getByText('Media')).toBeInTheDocument();
    expect(screen.getByText('Alta')).toBeInTheDocument();
    expect(screen.getByText('Confirmar lectura')).toBeInTheDocument();
  });

  it('shows filter tabs and filters correctly', () => {
    mockQueryData = [
      {
        id: 'a1', titulo: 'Aviso leído', contenido: 'Contenido',
        prioridad: 3, fecha_publicacion: '2025-06-01', require_ack: false, leido: true, vigencia_hasta: null,
      },
      {
        id: 'a2', titulo: 'Aviso no leído', contenido: 'No leído',
        prioridad: 1, fecha_publicacion: '2025-06-10', require_ack: true, leido: false, vigencia_hasta: null,
      },
    ];
    renderPage();

    expect(screen.getByText('Todos')).toBeInTheDocument();
    expect(screen.getByText('No leídos')).toBeInTheDocument();
    expect(screen.getByText('Leídos')).toBeInTheDocument();
  });

  it('renders empty state when no avisos', () => {
    mockQueryData = [];
    renderPage();

    expect(screen.getByText('No hay avisos activos')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });

  it('renders error state with retry button', () => {
    mockError = new Error('Error');
    renderPage();

    expect(screen.getByText('Error al cargar avisos')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });
});
