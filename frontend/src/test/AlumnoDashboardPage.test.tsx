import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

let mockData: Record<string, unknown> | null = null;
let mockIsLoading = false;
let mockError: Error | null = null;
const mockRefetch = vi.fn();

vi.mock('@/features/alumno/hooks/useAlumnoDashboard', () => ({
  useAlumnoDashboard: () => ({
    data: mockData,
    isLoading: mockIsLoading,
    error: mockError,
    refetch: mockRefetch,
  }),
}));

import { AlumnoDashboardPage } from '@/features/alumno/pages/AlumnoDashboardPage';

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AlumnoDashboardPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AlumnoDashboardPage', () => {
  beforeEach(() => {
    mockData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders dashboard with materias and alerts', () => {
    mockData = {
      materias: [
        { id: '1', nombre: 'Matemática', profesor: 'Prof. García', progreso: { aprobadas: 3, total: 5 }, estado: 'al_dia' },
        { id: '2', nombre: 'Lengua', profesor: 'Prof. López', progreso: { aprobadas: 1, total: 4 }, estado: 'atrasado' },
      ],
      avisos_no_leidos: 3,
      comunicaciones_no_leidas: 1,
      proximos_coloquios: [{ id: 'c1', materia_nombre: 'Matemática', fecha: '2025-07-15', cupos_restantes: 5 }],
      proximas_fechas: [{ id: 'f1', materia_nombre: 'Lengua', tipo: 'Parcial', fecha: '2025-06-20', descripcion: 'Parcial 2' }],
    };
    renderPage();

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Tenés 2 materias — 1 al día')).toBeInTheDocument();
    expect(screen.getAllByText('Matemática').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Lengua')).toBeInTheDocument();
    expect(screen.getByText('Al día')).toBeInTheDocument();
    expect(screen.getByText('Atrasado')).toBeInTheDocument();
    expect(screen.getByText('3 avisos no leídos')).toBeInTheDocument();

    expect(screen.getByText('Próximos coloquios')).toBeInTheDocument();
    expect(screen.getByText('Próximas fechas académicas')).toBeInTheDocument();
  });

  it('renders empty state when no materias', () => {
    mockData = {
      materias: [],
      avisos_no_leidos: 0,
      comunicaciones_no_leidas: 0,
      proximos_coloquios: [],
      proximas_fechas: [],
    };
    renderPage();

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('No estás inscripto en ninguna materia en este período')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });

  it('renders error state with retry button', () => {
    mockError = new Error('Network error');
    renderPage();

    expect(screen.getByText('Error al cargar el dashboard')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });
});
