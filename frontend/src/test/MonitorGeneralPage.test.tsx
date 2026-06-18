import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { MonitorGeneralPage } from '@/features/coordinacion/pages/MonitorGeneralPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        roles: ['ADMIN'],
        permissions: ['monitor:general:ver_todo'],
      },
    },
    hasPermission: (perm: string) => perm === 'monitor:general:ver_todo',
    hasAnyPermission: () => false,
  }),
}));

vi.mock('@/features/coordinacion/hooks/useMonitores', () => ({
  useMonitorGeneral: () => ({
    data: {
      data: {
        acciones_por_dia: [
          { fecha: '2024-01-01', cantidad: 10 },
          { fecha: '2024-01-02', cantidad: 15 },
          { fecha: '2024-01-03', cantidad: 8 },
        ],
        comunicaciones: [
          {
            docente_id: 'd1',
            docente_nombre: 'Juan Pérez',
            total_enviados: 20,
            pendientes: 5,
            ok: 12,
            fallidos: 3,
          },
          {
            docente_id: 'd2',
            docente_nombre: 'María García',
            total_enviados: 15,
            pendientes: 2,
            ok: 10,
            fallidos: 3,
          },
        ],
        interacciones: [
          {
            docente_id: 'd1',
            docente_nombre: 'Juan Pérez',
            materia_id: 'm1',
            materia_nombre: 'Matemática',
            acciones: { login: 5, upload: 3, view: 10 },
          },
        ],
        ultimas_acciones: [
          {
            id: 'log1',
            usuario_id: 'u1',
            usuario_nombre: 'Admin',
            accion: 'crear_asignacion',
            detalle: 'Asignación creada para Matemática',
            materia_id: 'm1',
            materia_nombre: 'Matemática',
            created_at: '2024-01-15T10:00:00Z',
          },
          {
            id: 'log2',
            usuario_id: 'u2',
            usuario_nombre: 'Coord',
            accion: 'eliminar_asignacion',
            detalle: undefined,
            materia_id: undefined,
            materia_nombre: undefined,
            created_at: '2024-01-15T11:00:00Z',
          },
        ],
      },
      total_acciones: 33,
    },
    isLoading: false,
    isError: false,
  }),
  useMonitorCoordinacion: () => ({
    data: null,
    isLoading: false,
  }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <MonitorGeneralPage />
    </TestWrapper>,
  );
}

describe('MonitorGeneralPage', () => {
  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Monitor General')).toBeInTheDocument();
    expect(
      screen.getByText('Panel de monitoreo general de actividad del sistema'),
    ).toBeInTheDocument();
  });

  it('renders chart section', () => {
    renderPage();
    expect(
      screen.getByText('Acciones por día (últimos 30 días)'),
    ).toBeInTheDocument();
    expect(screen.getByText('Total: 33 acciones registradas')).toBeInTheDocument();
  });

  it('renders communication table', () => {
    renderPage();
    expect(
      screen.getByText('Comunicaciones por docente'),
    ).toBeInTheDocument();
    expect(screen.getAllByText('Juan Pérez').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('María García')).toBeInTheDocument();
  });

  it('renders interacciones section', () => {
    renderPage();
    expect(
      screen.getByText('Interacciones por docente × materia'),
    ).toBeInTheDocument();
    expect(screen.getAllByText('Matemática').length).toBeGreaterThanOrEqual(1);
  });

  it('renders action log section', () => {
    renderPage();
    expect(screen.getByText('Últimas acciones')).toBeInTheDocument();
    expect(screen.getByText('crear_asignacion')).toBeInTheDocument();
    expect(screen.getByText('eliminar_asignacion')).toBeInTheDocument();
  });

  it('renders max log filter input', () => {
    renderPage();
    expect(screen.getByText('Máx registros:')).toBeInTheDocument();
    const logInput = screen.getByDisplayValue('200');
    expect(logInput).toBeInTheDocument();
  });

  it('shows admin view indicator', () => {
    renderPage();
    expect(
      screen.getByText('Mostrando datos de todo el tenant'),
    ).toBeInTheDocument();
  });

  it('shows interacciones action badges', () => {
    renderPage();
    expect(screen.getByText('login: 5')).toBeInTheDocument();
    expect(screen.getByText('upload: 3')).toBeInTheDocument();
    expect(screen.getByText('view: 10')).toBeInTheDocument();
  });

  it('handles undefined values in log table', () => {
    renderPage();
    const dashElements = screen.getAllByText('-');
    expect(dashElements.length).toBeGreaterThanOrEqual(2);
  });
});
