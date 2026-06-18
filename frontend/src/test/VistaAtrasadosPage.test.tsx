import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { VistaAtrasadosPage } from '@/features/academico/pages/VistaAtrasadosPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

vi.mock('@/features/academico/hooks/useAtrasados', () => ({
  useAtrasados: () => ({
    data: { alumnos: [], umbral: 60 },
    isLoading: false,
  }),
  useRanking: () => ({
    data: { alumnos: [] },
    isLoading: false,
  }),
  useNotasFinales: () => ({
    data: { alumnos: [] },
    isLoading: false,
  }),
  useReportesRapidos: () => ({
    data: null,
    isLoading: false,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/materias/123/atrasados']}>
        <Routes>
          <Route path="/materias/:id/atrasados" element={<VistaAtrasadosPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('VistaAtrasadosPage', () => {
  it('renders all sub-tabs', () => {
    renderPage();
    expect(screen.getByText('Atrasados')).toBeInTheDocument();
    expect(screen.getByText('Ranking')).toBeInTheDocument();
    expect(screen.getByText('Notas Finales')).toBeInTheDocument();
    expect(screen.getByText('Reportes')).toBeInTheDocument();
  });

  it('shows atrasados tab content by default', () => {
    renderPage();
    expect(screen.getByText('No hay alumnos atrasados en esta materia')).toBeInTheDocument();
  });

  it('switches to Ranking tab content', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByText('Ranking'));
    expect(screen.getByText('No hay datos de ranking disponibles')).toBeInTheDocument();
  });

  it('switches to Notas Finales tab', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByText('Notas Finales'));
    expect(screen.getByText('No hay notas finales disponibles')).toBeInTheDocument();
  });

  it('switches to Reportes tab', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByText('Reportes'));
    expect(screen.getByText('No hay datos importados para esta materia')).toBeInTheDocument();
  });
});
