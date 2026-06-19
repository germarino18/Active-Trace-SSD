import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { TwoFactorPage } from '@/features/auth/pages/TwoFactorPage';

const mockVerify2fa = vi.fn();

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: () => ({
    login: vi.fn(),
    verify2fa: mockVerify2fa,
    forgotPassword: vi.fn(),
    resetPassword: vi.fn(),
    logout: vi.fn(),
    hasPermission: vi.fn(),
    hasAnyPermission: vi.fn(),
    session: { status: 'unauthenticated' },
  }),
}));

describe('TwoFactorPage', () => {
  it('shows error when no challenge token', () => {
    render(
      <MemoryRouter initialEntries={['/2fa']}>
        <Routes>
          <Route path="/2fa" element={<TwoFactorPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText(/no hay una sesión de verificación/i)).toBeInTheDocument();
  });

  it('renders code input when token is present', () => {
    render(
      <MemoryRouter initialEntries={[{ pathname: '/2fa', state: { challengeToken: 'challenge-abc' } }]}>
        <Routes>
          <Route path="/2fa" element={<TwoFactorPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText(/verificación 2fa/i)).toBeInTheDocument();
    expect(screen.getAllByRole('textbox')).toHaveLength(6);
    expect(screen.getByRole('button', { name: /verificar/i })).toBeInTheDocument();
  });
});
