import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

let mockQueryData: unknown = null;
let mockIsLoading = false;
let mockError: Error | null = null;
const mockRefetch = vi.fn();

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
  };
});

import { MisColoquiosPage } from '@/features/alumno/pages/MisColoquiosPage';

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisColoquiosPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MisColoquiosPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders list of convocatorias with reservas', () => {
    mockQueryData = [
      {
        id: 'c1', materia_nombre: 'Matemática',
        fechas: [
          { fecha_id: 'f1', fecha: '2025-07-15', cupos_restantes: 5 },
          { fecha_id: 'f2', fecha: '2025-07-16', cupos_restantes: 3 },
        ],
        fecha_limite: '2025-07-10',
      },
      {
        id: 'c2', materia_nombre: 'Lengua',
        fechas: [
          { fecha_id: 'f3', fecha: '2025-07-20', cupos_restantes: 0 },
        ],
        fecha_limite: '2025-07-15',
      },
    ];
    renderPage();

    expect(screen.getByText('Coloquios')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Lengua')).toBeInTheDocument();
    expect(screen.getByText('2 fechas disponibles · 8 cupos')).toBeInTheDocument();
    expect(screen.getByText('1 fecha disponible · Sin cupos')).toBeInTheDocument();

    const buttons = screen.getAllByText('Reservar turno');
    expect(buttons.length).toBe(2);
    expect(buttons[0]).not.toBeDisabled();
    expect(buttons[1]).toBeDisabled();
  });

  it('renders empty state when no convocatorias', () => {
    mockQueryData = [];
    renderPage();

    expect(screen.getByText('No hay convocatorias de coloquio abiertas')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });

  it('renders error state with retry button', () => {
    mockError = new Error('Error');
    renderPage();

    expect(screen.getByText('Error al cargar convocatorias')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });
});
