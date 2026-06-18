import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { AuditoriaPage } from '@/features/admin/pages/AuditoriaPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['ADMIN'], permissions: ['auditoria:*'] } },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['ADMIN', 'auditoria:*'].includes(p)),
  }),
}));

const mockRegistros = [
  {
    id: 'r1', fecha: '2024-06-15T10:30:00Z', usuario_nombre: 'Juan Pérez',
    materia_nombre: 'Matemática', tipo_accion: 'crear', registros_afectados: 1,
    ip_origen: '192.168.1.1', agente_usuario: 'Mozilla/5.0',
    detalle: { campo: 'nombre', valor_anterior: 'MAT', valor_nuevo: 'MAT-101' },
  },
  {
    id: 'r2', fecha: '2024-06-14T09:00:00Z', usuario_nombre: 'María García',
    tipo_accion: 'login', ip_origen: '10.0.0.1',
  },
  {
    id: 'r3', fecha: '2024-06-13T15:45:00Z', usuario_nombre: 'Admin',
    materia_nombre: 'Física', tipo_accion: 'enviar_comunicacion', registros_afectados: 25,
    detalle: { tipo: 'recordatorio' },
  },
];

let mockAuditoriaState: Record<string, unknown> = {
  data: { items: mockRegistros, total: 3 },
  isLoading: false,
};

vi.mock('@/features/admin/hooks/useAuditoriaLog', () => ({
  useAuditoriaLog: () => mockAuditoriaState,
}));

function renderPage() {
  return render(
    <TestWrapper>
      <AuditoriaPage />
    </TestWrapper>,
  );
}

describe('AuditoriaPage', () => {
  afterEach(() => {
    mockAuditoriaState = { data: { items: mockRegistros, total: 3 }, isLoading: false };
  });

  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Auditoría')).toBeInTheDocument();
    expect(screen.getByText('Registro completo de actividades del sistema')).toBeInTheDocument();
  });

  it('renders filter inputs', () => {
    renderPage();
    expect(screen.getByText('Fecha desde')).toBeInTheDocument();
    expect(screen.getByText('Fecha hasta')).toBeInTheDocument();
    expect(screen.getByText('Tipo de acción')).toBeInTheDocument();
  });

  it('renders table with auditoria data', () => {
    renderPage();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('María García')).toBeInTheDocument();
    expect(screen.getByText('Admin')).toBeInTheDocument();
    expect(screen.getByText('Matemática')).toBeInTheDocument();
    expect(screen.getByText('Física')).toBeInTheDocument();
  });

  it('shows total count', () => {
    renderPage();
    expect(screen.getByText('3 registros')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockAuditoriaState = { data: undefined, isLoading: true };
    renderPage();
    expect(screen.getByText('Auditoría')).toBeInTheDocument();
  });

  it('shows empty state when no registros', () => {
    mockAuditoriaState = { data: { items: [], total: 0 }, isLoading: false };
    renderPage();
    expect(screen.getByText('No hay registros de auditoría')).toBeInTheDocument();
  });

  it('opens detail modal when clicking a row', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByText('Juan Pérez'));
    expect(screen.getByText('Detalle del registro')).toBeInTheDocument();
    expect(screen.getAllByText('192.168.1.1').length).toBe(2);
  });

  it('closes detail modal when clicking close', async () => {
    const user = userEvent.setup();
    renderPage();
    await user.click(screen.getByText('Juan Pérez'));
    expect(screen.getByText('Detalle del registro')).toBeInTheDocument();
    await user.click(screen.getByText('close'));
    expect(screen.queryByText('Detalle del registro')).not.toBeInTheDocument();
  });

  it('shows pagination controls', () => {
    mockAuditoriaState = { data: { items: mockRegistros, total: 150 }, isLoading: false };
    renderPage();
    expect(screen.getByText('Anterior')).toBeInTheDocument();
    expect(screen.getByText('Siguiente')).toBeInTheDocument();
  });
});
