import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

let mockQueryData: unknown = null;
let mockIsLoading = false;
let mockError: Error | null = null;
let mockQueryEnabled = true;
const mockRefetch = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: ({ enabled }: { enabled?: boolean }) => ({
      data: (enabled ?? true) ? mockQueryData : undefined,
      isLoading: (enabled ?? true) ? mockIsLoading : false,
      error: (enabled ?? true) ? mockError : null,
      refetch: mockRefetch,
    }),
  };
});

import { MisMateriasPage } from '@/features/alumno/pages/MisMateriasPage';
import { MateriaDetallePage } from '@/features/alumno/pages/MateriaDetallePage';

function renderMisMateriasPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisMateriasPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function renderMateriaDetallePage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/alumno/materias/123']}>
        <Routes>
          <Route path="/alumno/materias/:id" element={<MateriaDetallePage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MisMateriasPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders list of materias', () => {
    mockQueryData = [
      {
        id: '1', nombre: 'Matemática', profesor: 'Prof. García',
        actividades: [{ id: 'a1', nombre: 'TP1', nota: 8, estado: 'aprobado' }, { id: 'a2', nombre: 'TP2', nota: 6, estado: 'aprobado' }, { id: 'a3', nombre: 'TP3', nota: null, estado: 'pendiente' }],
        promedio: 7.5, condicion: 'regular',
      },
      {
        id: '2', nombre: 'Lengua', profesor: 'Prof. López',
        actividades: [{ id: 'b1', nombre: 'Examen', nota: 4, estado: 'desaprobado' }],
        promedio: null, condicion: 'libre',
      },
    ];
    renderMisMateriasPage();

    expect(screen.getByText('Mis Materias')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Lengua')).toBeInTheDocument();
    expect(screen.getByText('Regular')).toBeInTheDocument();
    expect(screen.getByText('Libre')).toBeInTheDocument();
    expect(screen.getByText('7.50')).toBeInTheDocument();
  });

  it('renders empty state when no materias', () => {
    mockQueryData = [];
    renderMisMateriasPage();

    expect(screen.getByText('No estás inscripto en ninguna materia')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderMisMateriasPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });
});

describe('MateriaDetallePage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders materia detail with actividades', () => {
    mockQueryData = {
      id: '123', nombre: 'Matemática', profesor: 'Prof. García',
      actividades: [
        { id: 'a1', nombre: 'TP1', nota: 8, estado: 'aprobado' },
        { id: 'a2', nombre: 'Examen Parcial', nota: 6, estado: 'pendiente' },
      ],
      promedio: 7.0, condicion: 'regular',
    };
    renderMateriaDetallePage();

    expect(screen.getAllByText('Matemática').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Prof. García')).toBeInTheDocument();
    expect(screen.getByText('Promedio general')).toBeInTheDocument();
    expect(screen.getByText('7.00')).toBeInTheDocument();
    expect(screen.getByText('TP1')).toBeInTheDocument();
    expect(screen.getByText('Examen Parcial')).toBeInTheDocument();
    expect(screen.getByText('Aprobado')).toBeInTheDocument();
    expect(screen.getByText('Pendiente')).toBeInTheDocument();
  });

  it('renders empty state when materia not found', () => {
    mockQueryData = null;
    renderMateriaDetallePage();

    expect(screen.getByText('Materia no encontrada')).toBeInTheDocument();
  });

  it('renders sin actividades message', () => {
    mockQueryData = {
      id: '123', nombre: 'Matemática', profesor: 'Prof. García',
      actividades: [],
      promedio: null, condicion: 'regular',
    };
    renderMateriaDetallePage();

    expect(screen.getAllByText('Matemática').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('No hay actividades registradas')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderMateriaDetallePage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });
});
