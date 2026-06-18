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

import { MisProgramasPage } from '@/features/alumno/pages/MisProgramasPage';
import { MisFechasPage } from '@/features/alumno/pages/MisFechasPage';

function renderMisProgramasPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisProgramasPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function renderMisFechasPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisFechasPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MisProgramasPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders programas list with download links', () => {
    mockQueryData = [
      {
        id: 'p1', materia_nombre: 'Matemática', programa_nombre: 'Programa 2025',
        fecha_publicacion: '2025-03-01', referencia_archivo: 'https://example.com/prog1.pdf',
      },
      {
        id: 'p2', materia_nombre: 'Lengua', programa_nombre: 'Programa 2025 v2',
        fecha_publicacion: '2025-04-01', referencia_archivo: null,
      },
    ];
    renderMisProgramasPage();

    expect(screen.getByText('Programas')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Lengua')).toBeInTheDocument();
    expect(screen.getByText('Descargar')).toBeInTheDocument();
    expect(screen.getByText('Sin archivo disponible')).toBeInTheDocument();
  });

  it('renders empty state when no programas', () => {
    mockQueryData = [];
    renderMisProgramasPage();

    expect(screen.getByText('No hay programas disponibles')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderMisProgramasPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });

  it('renders error state with retry button', () => {
    mockError = new Error('Error');
    renderMisProgramasPage();

    expect(screen.getByText('Error al cargar programas')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });
});

describe('MisFechasPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders fechas with tipo badges', () => {
    mockQueryData = [
      {
        id: 'f1', materia_nombre: 'Matemática', tipo: 'Parcial',
        fecha: '2025-06-15', descripcion: 'Primer Parcial',
      },
      {
        id: 'f2', materia_nombre: 'Lengua', tipo: 'TP',
        fecha: '2025-06-20', descripcion: 'Entrega TP Final',
      },
    ];
    renderMisFechasPage();

    expect(screen.getByText('Calendario Académico')).toBeInTheDocument();
    expect(screen.getByText('Primer Parcial')).toBeInTheDocument();
    expect(screen.getByText('Entrega TP Final')).toBeInTheDocument();
    expect(screen.getByText('Parcial')).toBeInTheDocument();
    expect(screen.getByText('TP')).toBeInTheDocument();
    expect(screen.getAllByText('Matemática').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Lengua').length).toBeGreaterThanOrEqual(1);
  });

  it('renders empty state when no fechas', () => {
    mockQueryData = [];
    renderMisFechasPage();

    expect(screen.getByText('No hay fechas académicas registradas')).toBeInTheDocument();
  });

  it('renders filter select for materias', () => {
    mockQueryData = [
      {
        id: 'f1', materia_nombre: 'Matemática', tipo: 'Parcial',
        fecha: '2025-06-15', descripcion: 'Primer Parcial',
      },
    ];
    renderMisFechasPage();

    expect(screen.getByText('Todas las materias')).toBeInTheDocument();
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderMisFechasPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });
});
