import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { FacturasPage } from '@/features/finanzas/pages/FacturasPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['FINANZAS'],
        permissions: ['FINANZAS', 'facturas:*', 'liquidaciones:*'],
      },
    },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['FINANZAS', 'ADMIN'].includes(p)),
  }),
}));

const mockUseFacturas = vi.fn();

vi.mock('@/features/finanzas/hooks/useFacturas', () => ({
  useFacturas: (...args: unknown[]) => mockUseFacturas(...args),
  useCrearFactura: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEditarFactura: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEliminarFactura: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useCambiarEstadoFactura: () => ({ mutate: vi.fn(), isPending: false }),
}));

const mockFacturas = {
  items: [
    {
      id: 'f1',
      docente_id: 'd1',
      docente_nombre: 'Juan Pérez',
      periodo: '2025-01',
      detalle: 'Honorarios enero 2025',
      archivo_nombre: 'factura.pdf',
      archivo_tamano: 102400,
      estado: 'pendiente' as const,
      fecha_carga: '2025-02-01T10:00:00Z',
    },
    {
      id: 'f2',
      docente_id: 'd2',
      docente_nombre: 'María García',
      periodo: '2025-01',
      detalle: 'Honorarios enero 2025',
      estado: 'abonada' as const,
      fecha_carga: '2025-02-01T11:00:00Z',
    },
  ],
  total: 2,
};

function renderPage() {
  return render(
    <TestWrapper>
      <FacturasPage />
    </TestWrapper>,
  );
}

describe('FacturasPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseFacturas.mockReturnValue({ data: mockFacturas, isLoading: false, isError: false });
  });

  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Facturas')).toBeInTheDocument();
    expect(screen.getByText('Gestioná las facturas de honorarios docentes')).toBeInTheDocument();
  });

  it('renders filter elements', () => {
    renderPage();
    expect(screen.getByPlaceholderText('Buscar por detalle, periodo...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Nombre del docente...')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Todos')).toBeInTheDocument();
  });

  it('renders factura table with data', () => {
    renderPage();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('María García')).toBeInTheDocument();
    expect(screen.getAllByText('2025-01').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('Abonada').length).toBeGreaterThanOrEqual(2);
  });

  it('renders Nueva factura button when canCreate is true', () => {
    renderPage();
    expect(screen.getByText('Nueva factura')).toBeInTheDocument();
  });

  it('renders loading state', () => {
    mockUseFacturas.mockReturnValue({ data: undefined, isLoading: true, isError: false });

    renderPage();
    expect(screen.getByText('Facturas')).toBeInTheDocument();
    expect(screen.queryByText('Juan Pérez')).not.toBeInTheDocument();
  });

  it('renders empty state when no facturas', () => {
    mockUseFacturas.mockReturnValue({ data: { items: [], total: 0 }, isLoading: false, isError: false });

    renderPage();
    expect(screen.getByText('No se encontraron facturas')).toBeInTheDocument();
  });

  it('renders error state', () => {
    mockUseFacturas.mockReturnValue({ data: undefined, isLoading: false, isError: true });

    renderPage();
    expect(screen.getByText('Error al cargar las facturas')).toBeInTheDocument();
  });
});
