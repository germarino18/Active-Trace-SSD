import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { MetricasPage } from '@/features/admin/pages/MetricasPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['ADMIN'], permissions: ['auditoria:*'] } },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['ADMIN', 'auditoria:*'].includes(p)),
  }),
}));

const mockDashboard = {
  total_docentes_activos: 45,
  total_comunicaciones: 1200,
  comunicaciones_ok: 980,
  comunicaciones_fallidas: 45,
};

const mockAcciones = [
  { fecha: '2024-06-10', total: 25 },
  { fecha: '2024-06-11', total: 32 },
  { fecha: '2024-06-12', total: 18 },
];

const mockEstados = [
  { estado: 'ok', cantidad: 980 },
  { estado: 'pendiente', cantidad: 175 },
  { estado: 'fallido', cantidad: 45 },
];

const mockInteracciones = [
  { docente_nombre: 'Juan Pérez', tipo_accion: 'crear', cantidad: 15 },
  { docente_nombre: 'María García', tipo_accion: 'actualizar', cantidad: 8 },
];

let mockDashboardState: Record<string, unknown> = {
  data: mockDashboard,
  isLoading: false,
};

let mockAccionesState: Record<string, unknown> = {
  data: mockAcciones,
  isLoading: false,
};

let mockEstadosState: Record<string, unknown> = {
  data: mockEstados,
  isLoading: false,
};

let mockInteraccionesState: Record<string, unknown> = {
  data: mockInteracciones,
  isLoading: false,
};

vi.mock('@/features/admin/hooks/useMetricas', () => ({
  useMetricasDashboard: () => mockDashboardState,
  useAccionesPorDia: () => mockAccionesState,
  useEstadosComunicacion: () => mockEstadosState,
  useInteracciones: () => mockInteraccionesState,
}));

function renderPage() {
  return render(
    <TestWrapper>
      <MetricasPage />
    </TestWrapper>,
  );
}

describe('MetricasPage', () => {
  afterEach(() => {
    mockDashboardState = { data: mockDashboard, isLoading: false };
    mockAccionesState = { data: mockAcciones, isLoading: false };
    mockEstadosState = { data: mockEstados, isLoading: false };
    mockInteraccionesState = { data: mockInteracciones, isLoading: false };
  });

  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Métricas')).toBeInTheDocument();
    expect(screen.getByText('Panel de indicadores y estadísticas del sistema')).toBeInTheDocument();
  });

  it('renders KPI cards with dashboard data', () => {
    renderPage();
    expect(screen.getByText('Docentes activos')).toBeInTheDocument();
    expect(screen.getByText('Comunicaciones totales')).toBeInTheDocument();
    expect(screen.getByText('Comunicaciones OK')).toBeInTheDocument();
    expect(screen.getByText('Comunicaciones fallidas')).toBeInTheDocument();
    expect(screen.getAllByText('45').length).toBe(3);
    expect(screen.getByText('1200')).toBeInTheDocument();
    expect(screen.getAllByText('980').length).toBe(2);
  });

  it('renders filter inputs', () => {
    renderPage();
    expect(screen.getByText('Fecha desde')).toBeInTheDocument();
    expect(screen.getByText('Fecha hasta')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('ID de materia...')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('ID o nombre...')).toBeInTheDocument();
  });

  it('renders chart components with data', () => {
    renderPage();
    expect(screen.getByText('Acciones por día')).toBeInTheDocument();
    expect(screen.getByText('Estado de comunicaciones')).toBeInTheDocument();
  });

  it('renders interacciones table', () => {
    renderPage();
    expect(screen.getByText('Interacciones por docente')).toBeInTheDocument();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('María García')).toBeInTheDocument();
  });

  it('shows loading state on KPIs', () => {
    mockDashboardState = { data: undefined, isLoading: true };
    renderPage();
    const skeleton = document.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('shows loading state on charts', () => {
    mockAccionesState = { data: undefined, isLoading: true };
    mockEstadosState = { data: undefined, isLoading: true };
    renderPage();
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('shows empty chart states when no data', () => {
    mockAccionesState = { data: [], isLoading: false };
    mockEstadosState = { data: [], isLoading: false };
    renderPage();
    expect(screen.getByText('Sin datos de actividades')).toBeInTheDocument();
    expect(screen.getByText('Sin comunicaciones')).toBeInTheDocument();
  });

  it('shows empty interacciones state', () => {
    mockInteraccionesState = { data: [], isLoading: false };
    renderPage();
    expect(screen.getByText('Sin interacciones registradas')).toBeInTheDocument();
  });
});
