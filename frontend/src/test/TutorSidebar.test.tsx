import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { Sidebar } from '@/features/layout/components/Sidebar';
import type { MenuItem } from '@/shared/types';

let mockPermissions: string[] = [];

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    session: {
      status: 'authenticated',
      user: {
        id: 'u1',
        nombre: 'Test',
        apellido: 'User',
        email: 'test@test.com',
        roles: [],
        permissions: mockPermissions,
        tenant_id: 't1',
      },
    },
    hasPermission: (perm: string) => mockPermissions.includes(perm),
    hasAnyPermission: (perms: string[]) => perms.some((p) => mockPermissions.includes(p)),
  }),
}));

vi.mock('@/features/layout/components/AppLayout', () => ({
  useSidebar: () => ({ isOpen: false, toggle: vi.fn(), close: vi.fn() }),
}));

const menuItems: MenuItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
  { label: 'Mis Alumnos', path: '/tutor/alumnos', icon: 'group', requiredPermissions: ['tutor:alumnos:ver'] },
  { label: 'Entregas sin corregir', path: '/entregas-sin-corregir', icon: 'assignment_late', requiredPermissions: ['tutor:entregas:ver'] },
  { label: 'Guardias', path: '/guardias', icon: 'shield', requiredPermissions: ['tutor:guardias:gestionar'] },
  { label: 'Equipos Docentes', path: '/equipos', icon: 'groups', requiredPermissions: ['equipos:ver'] },
  { label: 'Usuarios', path: '/admin/usuarios', icon: 'manage_accounts', requiredPermissions: ['usuarios:ver'] },
];

function renderSidebar() {
  return render(
    <MemoryRouter>
      <Sidebar menuItems={menuItems} />
    </MemoryRouter>,
  );
}

describe('TutorSidebar', () => {
  describe('with TUTOR permissions', () => {
    beforeEach(() => {
      mockPermissions = [
        'tutor:alumnos:ver',
        'tutor:entregas:ver',
        'tutor:guardias:gestionar',
      ];
    });

    it('shows tutor-specific items', () => {
      renderSidebar();
      expect(screen.getByText('Mis Alumnos')).toBeInTheDocument();
      expect(screen.getByText('Entregas sin corregir')).toBeInTheDocument();
      expect(screen.getByText('Guardias')).toBeInTheDocument();
    });

    it('does not show admin items without permission', () => {
      renderSidebar();
      expect(screen.queryByText('Usuarios')).not.toBeInTheDocument();
    });

    it('always shows Dashboard', () => {
      renderSidebar();
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  describe('with COORDINADOR/ADMIN permissions', () => {
    beforeEach(() => {
      mockPermissions = [
        'equipos:ver',
        'usuarios:ver',
        'tutor:alumnos:ver',
        'tutor:entregas:ver',
        'tutor:guardias:gestionar',
      ];
    });

    it('shows all items when user has permissions', () => {
      renderSidebar();
      expect(screen.getByText('Mis Alumnos')).toBeInTheDocument();
      expect(screen.getByText('Entregas sin corregir')).toBeInTheDocument();
      expect(screen.getByText('Guardias')).toBeInTheDocument();
      expect(screen.getByText('Equipos Docentes')).toBeInTheDocument();
      expect(screen.getByText('Usuarios')).toBeInTheDocument();
    });
  });
});
