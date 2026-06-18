import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { ForgotPasswordPage } from '@/features/auth/pages/ForgotPasswordPage';
import { TestWrapper } from './TestWrapper';

const mockForgotPassword = vi.fn();

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn(),
    verify2fa: vi.fn(),
    forgotPassword: mockForgotPassword,
    resetPassword: vi.fn(),
    logout: vi.fn(),
    hasPermission: vi.fn(),
    hasAnyPermission: vi.fn(),
    session: { status: 'unauthenticated' },
  }),
}));

describe('ForgotPasswordPage', () => {
  it('renders email field', () => {
    render(<ForgotPasswordPage />, { wrapper: TestWrapper });
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  });

  it('shows success message after submission', async () => {
    const user = userEvent.setup();
    mockForgotPassword.mockResolvedValue('Si el email existe, recibirá un enlace de recuperación');
    render(<ForgotPasswordPage />, { wrapper: TestWrapper });

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.click(screen.getByRole('button', { name: /enviar/i }));

    expect(await screen.findByText(/recibirá un enlace/i)).toBeInTheDocument();
  });
});
