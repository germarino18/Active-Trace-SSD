import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { AuthProvider } from '@/features/auth/context/AuthContext';
import { useAuth } from '@/features/auth/hooks/useAuth';

const mockRefreshToken = vi.fn();
const mockGetCurrentUser = vi.fn();

vi.mock('@/features/auth/services/auth.service', () => ({
  refreshToken: () => mockRefreshToken(),
  getCurrentUser: () => mockGetCurrentUser(),
  login: vi.fn(),
  verify2fa: vi.fn(),
  logout: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
}));

const TENANT_COOKIE = 'js-trace-tenant';
const RT_COOKIE = 'js-trace-rt';

function setAuthCookies(tenant: string, rt: string) {
  document.cookie = `${TENANT_COOKIE}=${encodeURIComponent(tenant)}; path=/`;
  document.cookie = `${RT_COOKIE}=${encodeURIComponent(rt)}; path=/`;
}

function clearAuthCookies() {
  document.cookie = `${TENANT_COOKIE}=; Max-Age=0; path=/`;
  document.cookie = `${RT_COOKIE}=; Max-Age=0; path=/`;
}

function SessionDisplay() {
  const { session } = useAuth();
  return <div data-testid="status">{session.status}</div>;
}

function renderWithProvider() {
  return render(
    <AuthProvider>
      <SessionDisplay />
    </AuthProvider>,
  );
}

const mockTokens = {
  access_token: 'tok',
  refresh_token: 'ref',
  expires_in: 900,
  token_type: 'bearer',
};

const mockUser = {
  id: '1',
  email: 'u@test.com',
  nombre: 'Test',
  apellido: 'User',
  roles: ['PROFESOR'],
  permissions: ['calificaciones:ver'],
  tenant_id: 'test',
};

describe('AuthProvider — session restoration', () => {
  beforeEach(() => {
    clearAuthCookies();
    mockRefreshToken.mockReset();
    mockGetCurrentUser.mockReset();
  });

  afterEach(() => {
    clearAuthCookies();
  });

  it('2.5 — restores session when both cookies exist and refresh succeeds', async () => {
    setAuthCookies('test', 'refresh-tok-123');
    mockRefreshToken.mockResolvedValue(mockTokens);
    mockGetCurrentUser.mockResolvedValue(mockUser);

    renderWithProvider();

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('authenticated');
    });

    expect(mockRefreshToken).toHaveBeenCalledOnce();
    expect(mockGetCurrentUser).toHaveBeenCalledOnce();
  });

  it('2.6 — immediately unauthenticated when no cookie exists', async () => {
    renderWithProvider();

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('unauthenticated');
    });

    expect(mockRefreshToken).not.toHaveBeenCalled();
  });

  it('2.7 — clears cookies and sets unauthenticated when refresh fails', async () => {
    setAuthCookies('test', 'refresh-tok-bad');
    mockRefreshToken.mockRejectedValue(new Error('401'));

    renderWithProvider();

    await waitFor(() => {
      expect(screen.getByTestId('status').textContent).toBe('unauthenticated');
    });

    // Both cookies should be gone
    expect(document.cookie).not.toContain(TENANT_COOKIE);
    expect(document.cookie).not.toContain(RT_COOKIE);
  });
});
