import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { UsuariosPage } from '@/features/admin/pages/UsuariosPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['ADMIN'], permissions: ['usuarios:gestionar'] } },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['ADMIN', 'usuarios:gestionar'].includes(p)),
  }),
}));

const mockUsuarios = [
  { id: '1', tenant_id: 't1', user_id: 'u1', nombre: 'Juan', apellidos: 'Pérez', banco: null, regional: 'CABA', legajo: 'L-001', legajo_profesional: null, facturador: false, estado: 'Activo', deleted_at: false },
  { id: '2', tenant_id: 't1', user_id: 'u2', nombre: 'María', apellidos: 'García', banco: null, regional: null, legajo: null, legajo_profesional: null, facturador: false, estado: 'Activo', deleted_at: false },
  { id: '3', tenant_id: 't1', user_id: 'u3', nombre: 'Carlos', apellidos: 'López', banco: null, regional: 'Rosario', legajo: null, legajo_profesional: null, facturador: true, estado: 'Inactivo', deleted_at: false },
];

let mockUsuariosState: Record<string, unknown> = {
  data: { items: mockUsuarios, total: 3 },
  isLoading: false,
  isError: false,
};

vi.mock('@/features/admin/hooks/useUsuarios', () => ({
  useUsuarios: () => mockUsuariosState,
  useCrearUsuario: () => ({ mutateAsync: vi.fn(), isPending: false }),
  useEditarUsuario: () => ({ mutateAsync: vi.fn(), isPending: false }),
}));

function renderPage() {
  return render(
    <TestWrapper>
      <UsuariosPage />
    </TestWrapper>,
  );
}

describe('UsuariosPage', () => {
  afterEach(() => {
    mockUsuariosState = { data: { items: mockUsuarios, total: 3 }, isLoading: false, isError: false };
  });

  it('renders page title and description', () => {
    renderPage();
    expect(screen.getByText('Usuarios')).toBeInTheDocument();
    expect(screen.getByText('Gestioná los usuarios del sistema')).toBeInTheDocument();
  });

  it('renders filter inputs', () => {
    renderPage();
    expect(screen.getByPlaceholderText('Buscar por nombre...')).toBeInTheDocument();
    expect(screen.getAllByText('Estado').length).toBeGreaterThanOrEqual(1);
  });

  it('renders table with usuarios data', () => {
    renderPage();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('María García')).toBeInTheDocument();
    expect(screen.getByText('Carlos López')).toBeInTheDocument();
    expect(screen.getByText('L-001')).toBeInTheDocument();
    expect(screen.getByText('CABA')).toBeInTheDocument();
    expect(screen.getByText('Rosario')).toBeInTheDocument();
  });

  it('renders estado badges and facturador indicator', () => {
    renderPage();
    expect(screen.getAllByText('Activo').length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText('Inactivo').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Sí')).toBeInTheDocument();
  });

  it('shows Nuevo usuario button for ADMIN', () => {
    renderPage();
    expect(screen.getByText('Nuevo usuario')).toBeInTheDocument();
  });

  it('shows loading state', () => {
    mockUsuariosState = { data: undefined, isLoading: true, isError: false };
    renderPage();
    expect(screen.getByText('Usuarios')).toBeInTheDocument();
  });

  it('shows error state', () => {
    mockUsuariosState = { data: undefined, isLoading: false, isError: true };
    renderPage();
    expect(screen.getByText('Error al cargar los usuarios')).toBeInTheDocument();
  });

  it('shows empty state when no usuarios', () => {
    mockUsuariosState = { data: { items: [], total: 0 }, isLoading: false, isError: false };
    renderPage();
    expect(screen.getByText('No se encontraron usuarios')).toBeInTheDocument();
  });
});
