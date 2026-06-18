import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';

const mockUseAuth = vi.fn();

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}));

import { PermissionGuard } from '@/features/auth/components/PermissionGuard';

describe('PermissionGuard', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders children when user has required permission', () => {
    mockUseAuth.mockReturnValue({
      session: { status: 'authenticated', user: { permissions: ['view:dashboard'] }, tokens: {} },
      hasPermission: (p: string) => p === 'view:dashboard',
      hasAnyPermission: (ps: string[]) => ps.includes('view:dashboard'),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <PermissionGuard permissions={['view:dashboard']}>
          <div>Granted Content</div>
        </PermissionGuard>
      </MemoryRouter>,
    );
    expect(screen.getByText('Granted Content')).toBeInTheDocument();
  });

  it('shows forbidden page when user lacks permission', () => {
    mockUseAuth.mockReturnValue({
      session: { status: 'authenticated', user: { permissions: [] }, tokens: {} },
      hasPermission: () => false,
      hasAnyPermission: () => false,
      logout: vi.fn(),
    });

    render(
      <MemoryRouter>
        <PermissionGuard permissions={['admin:system']}>
          <div>Granted Content</div>
        </PermissionGuard>
      </MemoryRouter>,
    );
    expect(screen.getByText(/no tiene permisos/i)).toBeInTheDocument();
  });
});
