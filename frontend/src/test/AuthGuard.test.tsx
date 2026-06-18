import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';

const mockUseAuth = vi.fn();

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => mockUseAuth(),
}));

import { AuthGuard } from '@/features/auth/components/AuthGuard';

describe('AuthGuard', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('redirects to login when no session', () => {
    mockUseAuth.mockReturnValue({
      session: { status: 'unauthenticated' },
      hasPermission: () => false,
      hasAnyPermission: () => false,
      login: vi.fn(),
      verify2fa: vi.fn(),
      forgotPassword: vi.fn(),
      resetPassword: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<AuthGuard />}>
            <Route path="/protected" element={<div>Protected</div>} />
          </Route>
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Login Page')).toBeInTheDocument();
  });

  it('renders children when session exists', () => {
    mockUseAuth.mockReturnValue({
      session: { status: 'authenticated', user: { permissions: ['view:dashboard'], nombre: 'Test', apellido: 'User', email: 'test@test.com', id: '1', roles: ['admin'], tenant_id: 't1' }, tokens: { access_token: 't', refresh_token: 'r', expires_in: 900, token_type: 'Bearer' } },
      hasPermission: () => true,
      hasAnyPermission: () => true,
      login: vi.fn(),
      verify2fa: vi.fn(),
      forgotPassword: vi.fn(),
      resetPassword: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route element={<AuthGuard />}>
            <Route path="/protected" element={<div>Protected Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});
