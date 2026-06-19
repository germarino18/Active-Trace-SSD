import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ComunicacionGeneralPage } from '@/features/academico/pages/ComunicacionGeneralPage';

vi.mock('@/shared/services/api', () => ({
  get: vi.fn(),
}));

import * as apiModule from '@/shared/services/api';
const mockGet = vi.mocked(apiModule.get);

const materias = [
  { id: 'm1', nombre: 'Matemáticas', codigo: 'MAT', comision: 'A', carrera: 'Ing', anio: 2024, cuatrimestre: 1, umbral: 60, created_at: '', updated_at: '' },
  { id: 'm2', nombre: 'Física', codigo: 'FIS', comision: 'B', carrera: 'Ing', anio: 2024, cuatrimestre: 1, umbral: 60, created_at: '', updated_at: '' },
];

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderPage() {
  return render(
    <QueryClientProvider client={makeQueryClient()}>
      <MemoryRouter initialEntries={['/comunicacion']}>
        <Routes>
          <Route path="/comunicacion" element={<ComunicacionGeneralPage />} />
          <Route path="/materias/:id/comunicar" element={<div data-testid="comunicar-page" />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ComunicacionGeneralPage', () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it('4.4/4.5 — shows materia rows with CTA buttons when materias exist', async () => {
    mockGet.mockResolvedValue(materias);

    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId('materia-row-m1')).toBeInTheDocument();
      expect(screen.getByTestId('materia-row-m2')).toBeInTheDocument();
    });

    expect(screen.getByText('Matemáticas')).toBeInTheDocument();
    expect(screen.getByText('Física')).toBeInTheDocument();
    expect(screen.getAllByText('Comunicar')).toHaveLength(2);
  });

  it('4.5 — shows empty state when no materias', async () => {
    mockGet.mockResolvedValue([]);

    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    expect(screen.getByText('Sin materias asignadas')).toBeInTheDocument();
  });

  it('CTA navigates to /materias/:id/comunicar', async () => {
    const user = userEvent.setup();
    mockGet.mockResolvedValue(materias);

    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId('comunicar-btn-m1')).toBeInTheDocument();
    });

    await user.click(screen.getByTestId('comunicar-btn-m1'));

    await waitFor(() => {
      expect(screen.getByTestId('comunicar-page')).toBeInTheDocument();
    });
  });
});
