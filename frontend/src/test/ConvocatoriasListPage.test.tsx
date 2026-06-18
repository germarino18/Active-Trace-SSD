import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConvocatoriasListPage } from '@/features/coordinacion/pages/ConvocatoriasListPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['COORDINADOR'],
        permissions: [
          'coordinacion:coloquios:crear',
          'coordinacion:coloquios:ver',
        ],
      },
    },
    hasPermission: (perm: string) =>
      ['coordinacion:coloquios:crear', 'coordinacion:coloquios:ver'].includes(perm),
    hasAnyPermission: () => false,
  }),
}));

vi.mock('@/features/coordinacion/hooks/useColoquios', () => ({
  useConvocatorias: () => ({
    data: {
      items: [
        {
          id: 'conv1',
          materia_id: 'm1',
          materia_nombre: 'Matemática',
          instancia: 1,
          dias: [
            {
              id: 'd1',
              fecha: '2024-02-01',
              hora_inicio: '09:00',
              hora_fin: '12:00',
              slots: 3,
              cupo_por_slot: 5,
            },
            {
              id: 'd2',
              fecha: '2024-02-03',
              hora_inicio: '09:00',
              hora_fin: '12:00',
              slots: 3,
              cupo_por_slot: 5,
            },
          ],
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
        },
        {
          id: 'conv2',
          materia_id: 'm2',
          materia_nombre: 'Física',
          instancia: 2,
          dias: [
            {
              id: 'd3',
              fecha: '2024-03-01',
              hora_inicio: '14:00',
              hora_fin: '17:00',
              slots: 2,
              cupo_por_slot: 4,
            },
          ],
          created_at: '2024-02-20T10:00:00Z',
          updated_at: '2024-02-20T10:00:00Z',
        },
      ],
      total: 2,
    },
    isLoading: false,
    isError: false,
  }),
  useConvocatoria: () => ({
    data: null,
    isLoading: false,
  }),
  useCrearConvocatoria: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useImportarAlumnos: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useMetricas: () => ({
    data: null,
    isLoading: false,
  }),
  useReservarTurno: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
  useResultados: () => ({
    data: [],
    isLoading: false,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ConvocatoriasListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('ConvocatoriasListPage', () => {
  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Convocatorias a Coloquios')).toBeInTheDocument();
    expect(
      screen.getByText('Gestioná las convocatorias a coloquios y exámenes orales.'),
    ).toBeInTheDocument();
  });

  it('renders materia names', () => {
    renderPage();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Física')).toBeInTheDocument();
  });

  it('renders instancia numbers', () => {
    renderPage();
    const allTwos = screen.getAllByText('2');
    const allOnes = screen.getAllByText('1');
    expect(allTwos.length + allOnes.length).toBeGreaterThanOrEqual(2);
  });

  it('renders cupos totales correctly (slots × cupo_por_slot per día)', () => {
    renderPage();
    expect(screen.getByText('30')).toBeInTheDocument(); // (3*5) + (3*5) = 30
    expect(screen.getByText('8')).toBeInTheDocument();  // (2*4) = 8
  });

  it('shows create button when user has permission', () => {
    renderPage();
    expect(screen.getByText('Nueva Convocatoria')).toBeInTheDocument();
  });

  it('shows Ver detalle links when user has permission', () => {
    renderPage();
    const detailLinks = screen.getAllByText('Ver detalle');
    expect(detailLinks.length).toBe(2);
  });
});
