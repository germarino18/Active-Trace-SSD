import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { TestWrapper } from './TestWrapper';
import { UsuariosPage } from '@/features/admin/pages/UsuariosPage';

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: { status: 'authenticated', user: { roles: ['ADMIN'], permissions: ['admin:usuarios:*'] } },
    hasPermission: () => true,
    hasAnyPermission: (perms: string[]) => perms.some((p) => ['ADMIN', 'admin:usuarios:*'].includes(p)),
  }),
}));

const mockUsuarios = [
  { id: '1', nombre: 'Juan', apellido: 'Pérez', email: 'juan@test.com', rol: 'ADMIN', activo: true, created_at: '2024-01-15' },
  { id: '2', nombre: 'María', apellido: 'García', email: 'maria@test.com', rol: 'PROFESOR', activo: true, created_at: '2024-02-20' },
  { id: '3', nombre: 'Carlos', apellido: 'López', email: 'carlos@test.com', rol: 'ALUMNO', activo: false, created_at: '2024-03-10' },
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
    expect(screen.getByPlaceholderText('Buscar por nombre o email...')).toBeInTheDocument();
    expect(screen.getAllByText('Rol').length).toBe(2);
    expect(screen.getAllByText('Estado').length).toBe(2);
  });

  it('renders table with usuarios data', () => {
    renderPage();
    expect(screen.getByText('Juan Pérez')).toBeInTheDocument();
    expect(screen.getByText('María García')).toBeInTheDocument();
    expect(screen.getByText('Carlos López')).toBeInTheDocument();
    expect(screen.getByText('juan@test.com')).toBeInTheDocument();
    expect(screen.getByText('maria@test.com')).toBeInTheDocument();
  });

  it('renders role badges and active/inactive status', () => {
    renderPage();
    expect(screen.getAllByText('Profesor').length).toBe(2);
    expect(screen.getAllByText('Alumno').length).toBe(2);
    expect(screen.getAllByText('Activo').length).toBe(3);
    expect(screen.getAllByText('Inactivo').length).toBe(2);
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
