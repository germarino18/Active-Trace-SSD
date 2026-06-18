import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
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

import { MisComunicacionesPage } from '@/features/alumno/pages/MisComunicacionesPage';
import { ComunicacionDetallePage } from '@/features/alumno/pages/ComunicacionDetallePage';

function renderMisComunicacionesPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <MisComunicacionesPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function renderComunicacionDetallePage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/alumno/comunicaciones/c1']}>
        <Routes>
          <Route path="/alumno/comunicaciones/:id" element={<ComunicacionDetallePage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MisComunicacionesPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders comunicaciones table with estados', () => {
    mockQueryData = [
      { id: 'c1', remitente: 'Dr. García', materia_nombre: 'Matemática', asunto: 'Aprobación de TP', fecha_envio: '2025-06-10', estado: 'Entregado' },
      { id: 'c2', remitente: 'Prof. López', materia_nombre: 'Lengua', asunto: 'Recordatorio final', fecha_envio: '2025-06-12', estado: 'Leido' },
    ];
    renderMisComunicacionesPage();

    expect(screen.getByText('Comunicaciones')).toBeInTheDocument();
    expect(screen.getByText('Dr. García')).toBeInTheDocument();
    expect(screen.getByText('Prof. López')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Lengua')).toBeInTheDocument();
    expect(screen.getByText('Aprobación de TP')).toBeInTheDocument();
    expect(screen.getByText('Recordatorio final')).toBeInTheDocument();
    expect(screen.getByText('Entregado')).toBeInTheDocument();
    expect(screen.getByText('Leido')).toBeInTheDocument();
  });

  it('renders empty state when no comunicaciones', () => {
    mockQueryData = [];
    renderMisComunicacionesPage();

    expect(screen.getByText('No tenés comunicaciones recibidas')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderMisComunicacionesPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });

  it('renders error state with retry button', () => {
    mockError = new Error('Error');
    renderMisComunicacionesPage();

    expect(screen.getByText('Error al cargar comunicaciones')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });
});

describe('ComunicacionDetallePage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders comunicacion detalle with all fields', () => {
    mockQueryData = {
      id: 'c1', asunto: 'Aprobación de TP', cuerpo: 'Te confirmo que tu TP fue aprobado con nota 8.',
      remitente: 'Dr. García', materia_nombre: 'Matemática',
      fecha_envio: '2025-06-10T14:00:00', estado_entrega: 'Entregado',
    };
    renderComunicacionDetallePage();

    expect(screen.getAllByText('Aprobación de TP').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Dr. García')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Entregado')).toBeInTheDocument();
    expect(screen.getByText('Te confirmo que tu TP fue aprobado con nota 8.')).toBeInTheDocument();
    expect(screen.getByText('Volver a comunicaciones')).toBeInTheDocument();
  });

  it('renders empty state when not found', () => {
    mockQueryData = null;
    renderComunicacionDetallePage();

    expect(screen.getByText('Comunicación no encontrada')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderComunicacionDetallePage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });
});
