import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { EncuentrosListPage } from '@/features/coordinacion/pages/EncuentrosListPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['COORDINADOR'],
        permissions: ['coordinacion:encuentros:crear'],
      },
    },
    hasPermission: (perm: string) => perm === 'coordinacion:encuentros:crear',
    hasAnyPermission: () => false,
  }),
}));

vi.mock('@/features/coordinacion/hooks/useEncuentros', () => ({
  useEncuentros: () => ({
    data: {
      items: [
        {
          id: 'e1',
          materia_id: 'm1',
          materia_nombre: 'Matemática',
          titulo: 'Clase 1: Funciones',
          fecha: '2024-03-01',
          hora_inicio: '09:00',
          hora_fin: '11:00',
          docente_id: 'd1',
          docente_nombre: 'Juan Pérez',
          estado: 'Pendiente' as const,
          url_meet: 'https://meet.google.com/abc',
          created_at: '2024-02-01',
          updated_at: '2024-02-01',
        },
        {
          id: 'e2',
          materia_id: 'm1',
          materia_nombre: 'Matemática',
          titulo: 'Clase 2: Límites',
          fecha: '2024-03-08',
          hora_inicio: '09:00',
          hora_fin: '11:00',
          docente_id: 'd1',
          docente_nombre: 'Juan Pérez',
          estado: 'Realizado' as const,
          url_meet: undefined,
          url_grabacion: 'https://drive.google.com/rec',
          created_at: '2024-02-01',
          updated_at: '2024-03-08',
        },
        {
          id: 'e3',
          materia_id: 'm2',
          materia_nombre: 'Física',
          titulo: 'Laboratorio 1',
          fecha: '2024-03-05',
          hora_inicio: '14:00',
          hora_fin: '17:00',
          docente_id: 'd2',
          docente_nombre: 'María García',
          estado: 'Cancelado' as const,
          url_meet: undefined,
          created_at: '2024-02-15',
          updated_at: '2024-03-04',
        },
      ],
      total: 3,
    },
    isLoading: false,
    isError: false,
  }),
  useEncuentro: () => ({
    data: null,
    isLoading: false,
  }),
  useCrearSlotRecurrente: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useCrearEncuentroUnico: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useActualizarInstancia: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useGenerarHtml: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <EncuentrosListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('EncuentrosListPage', () => {
  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Encuentros')).toBeInTheDocument();
    expect(
      screen.getByText('Administración de encuentros y clases en vivo.'),
    ).toBeInTheDocument();
  });

  it('renders filter inputs', () => {
    renderPage();
    expect(screen.getByPlaceholderText('Materia')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Docente')).toBeInTheDocument();
    expect(screen.getByText('Todos los estados')).toBeInTheDocument();
  });

  it('renders encuentro instances with date and time', () => {
    renderPage();
    expect(screen.getByText('Clase 1: Funciones')).toBeInTheDocument();
    expect(screen.getByText('Clase 2: Límites')).toBeInTheDocument();
    expect(screen.getByText('Laboratorio 1')).toBeInTheDocument();

    expect(screen.getByText('2024-03-01')).toBeInTheDocument();
    expect(screen.getByText('2024-03-08')).toBeInTheDocument();
    expect(screen.getByText('2024-03-05')).toBeInTheDocument();

    expect(screen.getAllByText('09:00 - 11:00').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('14:00 - 17:00')).toBeInTheDocument();
  });

  it('renders docente names', () => {
    renderPage();
    expect(screen.getAllByText('Juan Pérez').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('María García')).toBeInTheDocument();
  });

  it('renders state badges', () => {
    renderPage();
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Realizado').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Cancelado').length).toBeGreaterThanOrEqual(1);
  });

  it('shows meet link when url_meet is present', () => {
    renderPage();
    const meetLinks = screen.getAllByText('Abrir');
    expect(meetLinks.length).toBe(1);
  });

  it('shows create button when user has permission', () => {
    renderPage();
    expect(screen.getByText('Nuevo Encuentro')).toBeInTheDocument();
  });
});
