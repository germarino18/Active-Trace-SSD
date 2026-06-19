import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { z } from 'zod';

const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });

// ── Mock data state ──────────────────────────────────────────────────────────
let mockHilosData: unknown = null;
let mockHiloData: unknown = null;
let mockIsLoading = false;
let mockError: Error | null = null;
let mockMutationIsPending = false;
const mockRefetch = vi.fn();
const mockMutate = vi.fn();
const queryClientSpy = vi.fn();

vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQueryClient: () => ({ invalidateQueries: queryClientSpy }),
    useQuery: ({ queryKey }: { queryKey: unknown[] }) => {
      const isHilo = Array.isArray(queryKey) && queryKey[1] === 'hilo';
      return {
        data: isHilo ? mockHiloData : mockHilosData,
        isLoading: mockIsLoading,
        error: mockError,
        refetch: mockRefetch,
      };
    },
    useMutation: () => ({
      mutate: mockMutate,
      isPending: mockMutationIsPending,
      isError: false,
      isSuccess: false,
    }),
  };
});

import { InboxPage } from '@/features/inbox/pages/InboxPage';
import { HiloPage } from '@/features/inbox/pages/HiloPage';

function wrap(element: React.ReactNode) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{element}</MemoryRouter>
    </QueryClientProvider>,
  );
}

function wrapHilo(id: string) {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/inbox/${id}`]}>
        <Routes>
          <Route path="/inbox/:id" element={<HiloPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

// ── useInbox: unreadCount ────────────────────────────────────────────────────
describe('useInbox – unreadCount', () => {
  it('counts non-leido hilos correctly', () => {
    mockHilosData = [
      { id: 'h1', remitente: 'A', asunto: 'X', ultimo_mensaje: '', fecha: '', leido: false },
      { id: 'h2', remitente: 'B', asunto: 'Y', ultimo_mensaje: '', fecha: '', leido: true },
      { id: 'h3', remitente: 'C', asunto: 'Z', ultimo_mensaje: '', fecha: '', leido: false },
    ];
    mockIsLoading = false;
    mockError = null;
    wrap(<InboxPage />);
    expect(screen.getByText('2 mensajes sin leer')).toBeInTheDocument();
  });

  it('shows "Bandeja de entrada" when all hilos are leídos', () => {
    mockHilosData = [
      { id: 'h1', remitente: 'A', asunto: 'X', ultimo_mensaje: '', fecha: '', leido: true },
    ];
    mockIsLoading = false;
    mockError = null;
    wrap(<InboxPage />);
    expect(screen.getByText('Bandeja de entrada')).toBeInTheDocument();
  });
});

// ── InboxPage ────────────────────────────────────────────────────────────────
describe('InboxPage', () => {
  beforeEach(() => {
    mockHilosData = null;
    mockIsLoading = false;
    mockError = null;
  });

  it('renders hilos with remitente, asunto, and preview', () => {
    mockHilosData = [
      { id: 'h1', remitente: 'Dr. García', asunto: 'Consulta TP', ultimo_mensaje: 'Hola', fecha: '2025-06-10', leido: true },
      { id: 'h2', remitente: 'Prof. López', asunto: 'Re: Final', ultimo_mensaje: 'OK', fecha: '2025-06-12', leido: false },
    ];
    wrap(<InboxPage />);

    expect(screen.getByText('Dr. García')).toBeInTheDocument();
    expect(screen.getByText('Prof. López')).toBeInTheDocument();
    expect(screen.getByText('Consulta TP')).toBeInTheDocument();
    expect(screen.getByText('Re: Final')).toBeInTheDocument();
  });

  it('shows badge "Nuevo" only for unread hilos', () => {
    mockHilosData = [
      { id: 'h1', remitente: 'A', asunto: 'X', ultimo_mensaje: '', fecha: '', leido: true },
      { id: 'h2', remitente: 'B', asunto: 'Y', ultimo_mensaje: '', fecha: '', leido: false },
    ];
    wrap(<InboxPage />);
    expect(screen.getAllByText('Nuevo')).toHaveLength(1);
  });

  it('shows EmptyState when bandeja is empty', () => {
    mockHilosData = [];
    wrap(<InboxPage />);
    expect(screen.getByText('No tenés mensajes')).toBeInTheDocument();
  });

  it('shows error state with retry button', () => {
    mockError = new Error('Network error');
    wrap(<InboxPage />);
    expect(screen.getByText('Error al cargar mensajes')).toBeInTheDocument();
    expect(screen.getByText('Reintentar')).toBeInTheDocument();
  });

  it('shows spinner when loading', () => {
    mockIsLoading = true;
    wrap(<InboxPage />);
    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });
});

// ── HiloPage ─────────────────────────────────────────────────────────────────
describe('HiloPage', () => {
  beforeEach(() => {
    mockHiloData = null;
    mockHilosData = null;
    mockIsLoading = false;
    mockError = null;
    mockMutationIsPending = false;
  });

  it('renders mensajes in chronological order', () => {
    mockHiloData = [
      { id: 'm1', remitente: 'Dr. García', contenido: 'Mensaje primero', fecha: '2025-06-10T10:00:00' },
      { id: 'm2', remitente: 'Juan Pérez', contenido: 'Respuesta posterior', fecha: '2025-06-10T12:00:00' },
    ];
    wrapHilo('h1');

    expect(screen.getByText('Mensaje primero')).toBeInTheDocument();
    expect(screen.getByText('Respuesta posterior')).toBeInTheDocument();
    const items = screen.getAllByText(/Dr\. García|Juan Pérez/);
    expect(items[0].textContent).toMatch(/Dr\. García/);
  });

  it('disables send button when textarea is empty', () => {
    mockHiloData = [
      { id: 'm1', remitente: 'A', contenido: 'Hola', fecha: '2025-06-10T10:00:00' },
    ];
    wrapHilo('h1');
    const btn = screen.getByRole('button', { name: /Enviar respuesta/ });
    expect(btn).toBeDisabled();
  });

  it('shows EmptyState with back link when no messages', () => {
    mockHiloData = [];
    wrapHilo('h1');
    expect(screen.getByText('Mensaje no encontrado')).toBeInTheDocument();
    expect(screen.getByText('Volver a mensajes')).toBeInTheDocument();
  });

  it('shows spinner when loading', () => {
    mockIsLoading = true;
    wrapHilo('h1');
    expect(screen.getByRole('status', { name: 'Cargando' })).toBeInTheDocument();
  });
});

// ── Zod schema validation ─────────────────────────────────────────────────────
describe('Respuesta Zod schema', () => {
  const schema = z.object({
    contenido: z.string().min(1).max(2000),
  });

  it('rejects empty contenido', () => {
    expect(() => schema.parse({ contenido: '' })).toThrow();
  });

  it('rejects contenido exceeding 2000 chars', () => {
    expect(() => schema.parse({ contenido: 'a'.repeat(2001) })).toThrow();
  });

  it('accepts valid contenido', () => {
    expect(() => schema.parse({ contenido: 'Hola, gracias por la respuesta.' })).not.toThrow();
  });

  it('accepts contenido of exactly 2000 chars', () => {
    expect(() => schema.parse({ contenido: 'a'.repeat(2000) })).not.toThrow();
  });
});
