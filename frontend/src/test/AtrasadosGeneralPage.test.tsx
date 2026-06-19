import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AtrasadosGeneralPage } from '@/features/academico/pages/AtrasadosGeneralPage';

vi.mock('@/shared/services/api', () => ({
  get: vi.fn(),
}));

import * as apiModule from '@/shared/services/api';
const mockGet = vi.mocked(apiModule.get);

const materias = [
  { id: 'm1', nombre: 'Matemáticas', codigo: 'MAT', comision: 'A', carrera: 'Ing', anio: 2024, cuatrimestre: 1, umbral: 60, created_at: '', updated_at: '' },
  { id: 'm2', nombre: 'Física', codigo: 'FIS', comision: 'B', carrera: 'Ing', anio: 2024, cuatrimestre: 1, umbral: 60, created_at: '', updated_at: '' },
];

const alumnoAtrasado = {
  alumno: { id: 'a1', legajo: '001', nombre: 'Ana', apellido: 'García', email: 'ana@test.com', comision: 'A' },
  actividades_pendientes: 3,
  nota_actual: 4,
  porcentaje: 40,
  estado: 'atrasado' as const,
};

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderPage() {
  return render(
    <QueryClientProvider client={makeQueryClient()}>
      <MemoryRouter>
        <AtrasadosGeneralPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AtrasadosGeneralPage', () => {
  beforeEach(() => {
    mockGet.mockReset();
  });

  it('3.4 — renders combined table when materias have atrasados', async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes('mis-materias')) return Promise.resolve(materias);
      if (url.includes('m1')) return Promise.resolve({ materia_id: 'm1', umbral: 60, alumnos: [alumnoAtrasado], total: 1 });
      if (url.includes('m2')) return Promise.resolve({ materia_id: 'm2', umbral: 60, alumnos: [], total: 0 });
      return Promise.resolve([]);
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId('atrasados-table')).toBeInTheDocument();
    });

    expect(screen.getByText('García, Ana')).toBeInTheDocument();
    // "Matemáticas" appears in both the filter dropdown and the table row
    expect(screen.getAllByText('Matemáticas').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('40.0%')).toBeInTheDocument();
  });

  it('3.5 — shows empty state when no atrasados across all materias', async () => {
    mockGet.mockImplementation((url: string) => {
      if (url.includes('mis-materias')) return Promise.resolve(materias);
      return Promise.resolve({ materia_id: '', umbral: 60, alumnos: [], total: 0 });
    });

    renderPage();

    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });

    expect(screen.getByText(/No hay alumnos atrasados/)).toBeInTheDocument();
  });
});
