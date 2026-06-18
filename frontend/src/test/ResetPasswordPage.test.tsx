import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ResetPasswordPage } from '@/features/auth/pages/ResetPasswordPage';

const mockResetPassword = vi.fn();

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn(),
    verify2fa: vi.fn(),
    forgotPassword: vi.fn(),
    resetPassword: mockResetPassword,
    logout: vi.fn(),
    hasPermission: vi.fn(),
    hasAnyPermission: vi.fn(),
    session: { status: 'unauthenticated' },
  }),
}));

describe('ResetPasswordPage', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('shows error when no token in URL', () => {
    render(
      <MemoryRouter initialEntries={['/reset-password']}>
        <Routes>
          <Route path="/reset-password" element={<ResetPasswordPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText(/enlace inválido/i)).toBeInTheDocument();
  });

  it('submits valid passwords and shows success', async () => {
    const user = userEvent.setup();
    mockResetPassword.mockResolvedValue('Contraseña actualizada correctamente');

    render(
      <MemoryRouter initialEntries={['/reset-password?token=valid-token-123']}>
        <Routes>
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>,
    );

    const inputs = screen.getAllByPlaceholderText('••••••••');
    const passwordInput = inputs[0]!;
    const confirmInput = inputs[1]!;

    await user.type(passwordInput, 'newpassword123');
    await user.type(confirmInput, 'newpassword123');
    await user.click(screen.getByRole('button', { name: /restablecer/i }));

    expect(await screen.findByText(/actualizada correctamente/i)).toBeInTheDocument();
  });
});
