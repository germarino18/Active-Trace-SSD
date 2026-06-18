import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { LoginPage } from '@/features/auth/pages/LoginPage';

const mockLogin = vi.fn();

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
    verify2fa: vi.fn(),
    forgotPassword: vi.fn(),
    resetPassword: vi.fn(),
    logout: vi.fn(),
    hasPermission: vi.fn(),
    hasAnyPermission: vi.fn(),
    session: { status: 'unauthenticated' },
  }),
}));

function renderLoginPage(route = '/login') {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<div>Dashboard</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('LoginPage', () => {
  beforeEach(() => {
    mockLogin.mockReset();
  });

  it('renders all form fields (email, password, tenant)', () => {
    renderLoginPage();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tenant/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
  });

  it('submits login form with valid data and navigates on success', async () => {
    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'password123');
    await user.type(screen.getByLabelText(/tenant/i), 'test-tenant');

    mockLogin.mockResolvedValue({ access_token: 'token', expires_in: 900 });

    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    await vi.waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123', 'test-tenant');
    });
  });

  it('displays error message on invalid credentials', async () => {
    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText(/email/i), 'wrong@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'wrongpassword');
    await user.type(screen.getByLabelText(/tenant/i), 'test-tenant');

    mockLogin.mockRejectedValue({
      response: { data: { error: { message: 'Credenciales inválidas' } } },
    });

    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    expect(await screen.findByText(/credenciales inválidas/i)).toBeInTheDocument();
  });

  it('shows 2FA form when challenge is returned', async () => {
    const user = userEvent.setup();
    renderLoginPage();

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/contraseña/i), 'password123');
    await user.type(screen.getByLabelText(/tenant/i), 'test-tenant');

    mockLogin.mockResolvedValue({
      requires_2fa: true,
      challenge_token: 'challenge-abc',
    });

    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    expect(await screen.findByText(/verificación en dos pasos/i)).toBeInTheDocument();
  });
});
