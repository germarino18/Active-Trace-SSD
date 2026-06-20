import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AvisosListPage } from '@/features/coordinacion/pages/AvisosListPage';

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
          'avisos:publicar',
        ],
      },
    },
    hasPermission: () => true,
    hasAnyPermission: () => true,
  }),
}));

vi.mock('@/features/coordinacion/hooks/useAvisos', () => ({
  useAvisos: () => ({
    data: [
      {
        id: 'a1',
        tenant_id: 't1',
        titulo: 'Recordatorio carga actas',
        cuerpo: 'Completar actas pendientes',
        alcance: 'GLOBAL' as const,
        severidad: 'ADVERTENCIA' as const,
        inicio_en: '2024-01-01T00:00:00Z',
        fin_en: '2024-12-31T00:00:00Z',
        requiere_ack: true,
        orden: 1,
        activo: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 'a2',
        tenant_id: 't1',
        titulo: 'Cambio de programa',
        cuerpo: 'Programa actualizado',
        alcance: 'POR_MATERIA' as const,
        materia_id: 'mat-123',
        severidad: 'INFO' as const,
        inicio_en: '2024-02-01T00:00:00Z',
        fin_en: '2024-03-01T00:00:00Z',
        requiere_ack: false,
        orden: 2,
        activo: true,
        created_at: '2024-02-01T00:00:00Z',
        updated_at: '2024-02-01T00:00:00Z',
      },
      {
        id: 'a3',
        tenant_id: 't1',
        titulo: 'Urgente: Paro docente',
        cuerpo: 'Suspensión de actividades',
        alcance: 'POR_ROL' as const,
        rol_destino: 'PROFESOR',
        severidad: 'CRITICO' as const,
        inicio_en: '2024-03-01T00:00:00Z',
        fin_en: '2024-03-05T00:00:00Z',
        requiere_ack: true,
        orden: 3,
        activo: true,
        created_at: '2024-03-01T00:00:00Z',
        updated_at: '2024-03-01T00:00:00Z',
      },
    ],
    isLoading: false,
    isError: false,
  }),
  useAviso: () => ({
    data: null,
    isLoading: false,
  }),
  useCrearAviso: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
    isError: false,
  }),
  useActualizarAviso: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
  useEliminarAviso: () => ({
    mutate: vi.fn(),
    isPending: false,
  }),
}));

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <AvisosListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('AvisosListPage', () => {
  it('renders page title', () => {
    renderPage();
    expect(screen.getByText('Avisos')).toBeInTheDocument();
  });

  it('shows scope labels correctly', () => {
    renderPage();
    expect(screen.getByText('Global')).toBeInTheDocument();
    expect(screen.getByText('Materia (mat-123)')).toBeInTheDocument();
    expect(screen.getByText('Rol (PROFESOR)')).toBeInTheDocument();
  });

  it('shows severity badges', () => {
    renderPage();
    expect(screen.getByText('Advertencia')).toBeInTheDocument();
    expect(screen.getByText('Info')).toBeInTheDocument();
    expect(screen.getByText('Crítico')).toBeInTheDocument();
  });

  it('shows aviso titles', () => {
    renderPage();
    expect(screen.getByText('Recordatorio carga actas')).toBeInTheDocument();
    expect(screen.getByText('Cambio de programa')).toBeInTheDocument();
    expect(screen.getByText('Urgente: Paro docente')).toBeInTheDocument();
  });

  it('shows create button for users with publicar permission', () => {
    renderPage();
    expect(screen.getByText('Nuevo Aviso')).toBeInTheDocument();
  });

  it('shows edit buttons for admin users', () => {
    renderPage();
    const editLinks = screen.getAllByRole('link', { name: /edit/i });
    expect(editLinks.length).toBe(3);
  });
});
