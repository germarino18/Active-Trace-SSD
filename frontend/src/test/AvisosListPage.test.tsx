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
          'coordinacion:avisos:admin',
          'coordinacion:avisos:crear',
        ],
      },
    },
    hasPermission: () => true,
    hasAnyPermission: () => true,
  }),
}));

const mockConfirmarAck = { mutate: vi.fn(), isPending: false };

vi.mock('@/features/coordinacion/hooks/useAvisos', () => ({
  useAvisos: () => ({
    data: {
      items: [
        {
          id: 'a1',
          tenant_id: 't1',
          titulo: 'Recordatorio carga actas',
          mensaje: 'Completar actas pendientes',
          scope: 'Global' as const,
          scope_value: undefined,
          severidad: 'warning' as const,
          vigencia_desde: '2024-01-01',
          vigencia_hasta: '2024-12-31',
          requiere_ack: true,
          orden: 1,
          created_by: 'admin',
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
          total_acks: 50,
          ack_count: 30,
          user_acked: false,
        },
        {
          id: 'a2',
          tenant_id: 't1',
          titulo: 'Cambio de programa',
          mensaje: 'Programa actualizado',
          scope: 'Materia' as const,
          scope_value: 'Matemática',
          severidad: 'info' as const,
          vigencia_desde: '2024-02-01',
          vigencia_hasta: '2024-03-01',
          requiere_ack: false,
          orden: 2,
          created_by: 'coord',
          created_at: '2024-02-01',
          updated_at: '2024-02-01',
          total_acks: 0,
          ack_count: 0,
          user_acked: true,
        },
        {
          id: 'a3',
          tenant_id: 't1',
          titulo: 'Urgente: Paro docente',
          mensaje: 'Suspensión de actividades',
          scope: 'Rol' as const,
          scope_value: 'PROFESOR',
          severidad: 'critical' as const,
          vigencia_desde: '2024-03-01',
          vigencia_hasta: '2024-03-05',
          requiere_ack: true,
          orden: 3,
          created_by: 'admin',
          created_at: '2024-03-01',
          updated_at: '2024-03-01',
          total_acks: 100,
          ack_count: 80,
          user_acked: false,
        },
      ],
      total: 3,
    },
    isLoading: false,
    isError: false,
  }),
  useConfirmarAck: () => mockConfirmarAck,
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
    expect(screen.getByText('Materia (Matemática)')).toBeInTheDocument();
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

  it('shows ack counters for admin users', () => {
    renderPage();
    expect(screen.getByText('30/50 confirmado(s)')).toBeInTheDocument();
    expect(screen.getByText('80/100 confirmado(s)')).toBeInTheDocument();
  });

  it('shows "Confirmar lectura" button for unacknowledged avisos', () => {
    renderPage();
    const confirmButtons = screen.getAllByText('Confirmar lectura');
    expect(confirmButtons.length).toBe(2);
  });

  it('shows "✓ Leído" for acknowledged avisos', () => {
    renderPage();
    expect(screen.getAllByText('✓ Leído').length).toBe(1);
  });

  it('shows create button for users with crear permission', () => {
    renderPage();
    expect(screen.getByText('Nuevo Aviso')).toBeInTheDocument();
  });
});
