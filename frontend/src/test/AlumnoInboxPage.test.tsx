import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

let mockQueryData: unknown = null;
let mockIsLoading = false;
let mockError: Error | null = null;
let mockMutationIsPending = false;
const mockRefetch = vi.fn();
const mockMutate = vi.fn();
const mockReset = vi.fn();
const queryClientSpy = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQueryClient: () => ({ invalidateQueries: queryClientSpy }),
    useQuery: () => ({
      data: mockQueryData,
      isLoading: mockIsLoading,
      error: mockError,
      refetch: mockRefetch,
    }),
    useMutation: () => ({
      mutate: mockMutate,
      isPending: mockMutationIsPending,
      isError: false,
      isSuccess: false,
      reset: mockReset,
    }),
  };
});

import { AlumnoInboxPage } from '@/features/alumno/pages/AlumnoInboxPage';
import { AlumnoHiloPage } from '@/features/alumno/pages/AlumnoHiloPage';

function renderInboxPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AlumnoInboxPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function renderHiloPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/alumno/inbox/h1']}>
        <Routes>
          <Route path="/alumno/inbox/:id" element={<AlumnoHiloPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AlumnoInboxPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders hilos list with remitente and asunto', () => {
    mockQueryData = [
      { id: 'h1', remitente: 'Dr. García', asunto: 'Consulta sobre TP', ultimo_mensaje: 'Te respondí la consulta', fecha: '2025-06-10', leido: true },
      { id: 'h2', remitente: 'Prof. López', asunto: 'Re: Entrega final', ultimo_mensaje: 'Recibí tu trabajo', fecha: '2025-06-12', leido: false },
    ];
    renderInboxPage();

    expect(screen.getByText('Mensajes')).toBeInTheDocument();
    expect(screen.getByText('Dr. García')).toBeInTheDocument();
    expect(screen.getByText('Prof. López')).toBeInTheDocument();
    expect(screen.getByText('Consulta sobre TP')).toBeInTheDocument();
    expect(screen.getByText('Re: Entrega final')).toBeInTheDocument();
    expect(screen.getByText('Te respondí la consulta')).toBeInTheDocument();
    expect(screen.getByText('Recibí tu trabajo')).toBeInTheDocument();
  });

  it('renders empty state when no hilos', () => {
    mockQueryData = [];
    renderInboxPage();

    expect(screen.getByText('No tenés mensajes')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderInboxPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });

  it('renders error state with retry button', () => {
    mockError = new Error('Error');
    renderInboxPage();

    expect(screen.getByText('Error al cargar mensajes')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });
});

describe('AlumnoHiloPage', () => {
  beforeEach(() => {
    mockQueryData = null;
    mockIsLoading = false;
    mockError = null;
    mockMutationIsPending = false;
  });

  it('renders messages in a hilo', () => {
    mockQueryData = [
      { id: 'm1', remitente: 'Dr. García', contenido: 'Hola, te respondo la consulta sobre el TP', fecha: '2025-06-10T10:00:00' },
      { id: 'm2', remitente: 'Juan Pérez', contenido: 'Gracias, ya lo revisé', fecha: '2025-06-10T12:00:00' },
    ];
    renderHiloPage();

    expect(screen.getAllByText('Dr. García').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Hola, te respondo la consulta sobre el TP')).toBeInTheDocument();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('Gracias, ya lo revisé')).toBeInTheDocument();

    expect(screen.getByPlaceholderText('Escribí tu respuesta...')).toBeInTheDocument();
    expect(screen.getByText('Enviar respuesta')).toBeInTheDocument();
    expect(screen.getByText('Volver')).toBeInTheDocument();
  });

  it('renders empty state when no messages found', () => {
    mockQueryData = [];
    renderHiloPage();

    expect(screen.getByText('No se encontró el hilo')).toBeInTheDocument();
  });

  it('renders spinner when loading', () => {
    mockIsLoading = true;
    renderHiloPage();

    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });
});
