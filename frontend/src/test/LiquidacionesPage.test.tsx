import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { LiquidacionesPage } from '@/features/finanzas/pages/LiquidacionesPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['FINANZAS'],
        permissions: ['FINANZAS', 'liquidaciones:*', 'facturas:*'],
      },
    },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['FINANZAS', 'ADMIN'].includes(p)),
  }),
}));

const mockUseLiquidacion = vi.fn();
const mockUseLiquidacionKPIs = vi.fn();
const mockUseHistorial = vi.fn();

vi.mock('@/features/finanzas/hooks/useLiquidaciones', () => ({
  useLiquidacion: (...args: unknown[]) => mockUseLiquidacion(...args),
  useLiquidacionKPIs: (...args: unknown[]) => mockUseLiquidacionKPIs(...args),
  useHistorial: (...args: unknown[]) => mockUseHistorial(...args),
  useCerrarLiquidacion: () => ({
    mutateAsync: vi.fn(),
    isPending: false,
  }),
}));

const mockLiquidacion = {
  periodo: '2025-01',
  segmento: 'general' as const,
  docentes: [
    {
      id: '1',
      docente_nombre: 'Juan',
      docente_apellido: 'Pérez',
      rol: 'PROFESOR',
      comisiones: 2,
      salario_base: 500000,
      plus: 100000,
      total: 600000,
    },
    {
      id: '2',
      docente_nombre: 'María',
      docente_apellido: 'García',
      rol: 'TUTOR',
      comisiones: 1,
      salario_base: 300000,
      plus: 50000,
      total: 350000,
    },
  ],
  total_docentes: 2,
  monto_total: 950000,
  cerrada: false,
};

const mockKPIs = {
  total_docentes: 2,
  monto_total: 950000,
  facturas_pendientes: 1,
  periodos_cerrados: 3,
};

const mockHistorial = [
  {
    periodo: '2024-12',
    cerrada_en: '2024-12-15T10:00:00Z',
    total_docentes: 10,
    monto_total: 5000000,
  },
];

beforeEach(() => {
  vi.clearAllMocks();
  mockUseLiquidacion.mockReturnValue({ data: mockLiquidacion, isLoading: false });
  mockUseLiquidacionKPIs.mockReturnValue({ data: mockKPIs, isLoading: false });
  mockUseHistorial.mockReturnValue({ data: mockHistorial, isLoading: false });
});

function renderPage() {
  return render(
    <TestWrapper>
      <LiquidacionesPage />
    </TestWrapper>,
  );
}

describe('LiquidacionesPage', () => {
  it('renders page title and period description', () => {
    renderPage();
    expect(screen.getByText('Liquidaciones')).toBeInTheDocument();
    expect(screen.getByText(/Gestioná las liquidaciones del período/)).toBeInTheDocument();
    expect(screen.getByText(/2025-01/)).toBeInTheDocument();
  });

  it('renders segment tabs', () => {
    renderPage();
    expect(screen.getByRole('tab', { name: 'General' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'NEXO' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'Factura' })).toBeInTheDocument();
  });

  it('renders KPI cards', () => {
    renderPage();
    expect(screen.getByText('Total docentes')).toBeInTheDocument();
    expect(screen.getByText('Monto total')).toBeInTheDocument();
    expect(screen.getByText('Facturas pendientes')).toBeInTheDocument();
    expect(screen.getByText('Períodos cerrados')).toBeInTheDocument();
  });

  it('renders liquidacion table with data', () => {
    renderPage();
    expect(screen.getByText('Pérez, Juan')).toBeInTheDocument();
    expect(screen.getByText('García, María')).toBeInTheDocument();
    expect(screen.getByText('PROFESOR')).toBeInTheDocument();
    expect(screen.getByText('TUTOR')).toBeInTheDocument();
  });

  it('renders exportar and cerrar liquidacion buttons when liquidacion is not closed', () => {
    renderPage();
    expect(screen.getByText('Exportar')).toBeInTheDocument();
    expect(screen.getByText('Cerrar liquidación')).toBeInTheDocument();
  });

  it('renders loading state without data', () => {
    mockUseLiquidacion.mockReturnValue({ data: undefined, isLoading: true });
    mockUseLiquidacionKPIs.mockReturnValue({ data: undefined, isLoading: true });
    mockUseHistorial.mockReturnValue({ data: undefined, isLoading: true });

    renderPage();
    expect(screen.getByText('Liquidaciones')).toBeInTheDocument();
    expect(screen.queryByText('Pérez, Juan')).not.toBeInTheDocument();
  });
});
