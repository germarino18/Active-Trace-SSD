import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MonitorSeguimientoPage } from '@/features/academico/pages/MonitorSeguimientoPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

vi.mock('@/features/academico/hooks/useMonitor', () => ({
  useMonitor: () => ({
    filters: {},
    updateFilter: vi.fn(),
    applyFilters: vi.fn(),
    clearFilters: vi.fn(),
    query: {
      data: null,
      isLoading: false,
      isError: false,
      error: null,
    },
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/materias/123/monitor']}>
        <Routes>
          <Route path="/materias/:id/monitor" element={<MonitorSeguimientoPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MonitorSeguimientoPage', () => {
  it('renders filter inputs', () => {
    renderPage();
    expect(screen.getByText('Monitor de Seguimiento')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Buscar por nombre...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ej: A, B, C...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Nombre de actividad...')).toBeInTheDocument();
  });

  it('renders apply and clear filter buttons', () => {
    renderPage();
    expect(screen.getByText('Aplicar filtros')).toBeInTheDocument();
    expect(screen.getByText('Limpiar filtros')).toBeInTheDocument();
  });

  it('shows empty state when no data', () => {
    renderPage();
    expect(screen.getByText('No se encontraron alumnos con los filtros seleccionados')).toBeInTheDocument();
  });

  it('renders filter labels', () => {
    renderPage();
    expect(screen.getByText('Alumno')).toBeInTheDocument();
    expect(screen.getByText('Comisión')).toBeInTheDocument();
    expect(screen.getByText('Actividad')).toBeInTheDocument();
    expect(screen.getByText('Completitud mín. (%)')).toBeInTheDocument();
  });
});
