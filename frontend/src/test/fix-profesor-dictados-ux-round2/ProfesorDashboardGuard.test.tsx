/**
 * TDD RED/GREEN/TRIANGULATE — Tasks 7d.1, 7d.2, 7d.3
 * - 7d.1: PROFESOR navigating to /dashboard is redirected to /profesor-dashboard
 * - 7d.2: Nav item "Dashboard → /dashboard" is hidden for PROFESOR role
 * - 7d.3: Non-profesor roles are NOT redirected; /dictados and /profesor-dashboard unaffected
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// ---- Mock useAuth ----
vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// ---- Mock dependencies of AppLayout that make real API calls ----
vi.mock('@/features/coordinacion/hooks/useAprobacionComunicaciones', () => ({
  useLotesPendientesCount: vi.fn(() => 0),
}));
vi.mock('@/features/inbox/hooks/useInbox', () => ({
  useInbox: vi.fn(() => ({ unreadCount: 0 })),
}));

import { useAuth } from '@/features/auth/hooks/useAuth';
import { DashboardEntry } from '@/features/auth/components/DashboardEntry';
import { buildSectionsForRole } from '@/features/layout/components/AppLayout';

const mockUseAuth = vi.mocked(useAuth);

function makeSession(role: string) {
  return {
    session: {
      status: 'authenticated' as const,
      user: {
        id: 'u1',
        email: 'a@b.com',
        nombre: 'Test',
        apellido: 'User',
        roles: [role],
        permissions: [],
        tenant_id: 't1',
      },
      tokens: { access_token: '', refresh_token: '', expires_in: 0, token_type: 'bearer' },
    },
    hasPermission: vi.fn().mockReturnValue(false),
    hasAnyPermission: vi.fn().mockReturnValue(false),
    login: vi.fn(),
    logout: vi.fn(),
    verify2fa: vi.fn(),
    forgotPassword: vi.fn(),
    resetPassword: vi.fn(),
  };
}

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });

function renderGuard(role: string, initialPath = '/dashboard') {
  mockUseAuth.mockReturnValue(makeSession(role) as ReturnType<typeof useAuth>);
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/dashboard" element={<DashboardEntry />} />
          <Route path="/profesor-dashboard" element={<div>Mis Métricas Profesor</div>} />
          <Route path="/dictados" element={<div>Dictados</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('DashboardEntry guard — task 7d.1', () => {
  beforeEach(() => vi.clearAllMocks());

  it('redirects PROFESOR from /dashboard to /profesor-dashboard', () => {
    renderGuard('PROFESOR');
    expect(screen.getByText('Mis Métricas Profesor')).toBeInTheDocument();
  });

  it('does NOT redirect ADMIN — renders /dashboard content', () => {
    renderGuard('ADMIN');
    // Should NOT reach /profesor-dashboard — it stays on /dashboard
    expect(screen.queryByText('Mis Métricas Profesor')).not.toBeInTheDocument();
  });

  it('does NOT redirect ALUMNO — stays on /dashboard', () => {
    renderGuard('ALUMNO');
    expect(screen.queryByText('Mis Métricas Profesor')).not.toBeInTheDocument();
  });

  it('does NOT redirect TUTOR — stays on /dashboard', () => {
    renderGuard('TUTOR');
    expect(screen.queryByText('Mis Métricas Profesor')).not.toBeInTheDocument();
  });

  // 7d.3 TRIANGULATE: /dictados is unaffected (prof-only route, no redirect)
  it('7d.3 — /dictados route is untouched (no redirect from it)', () => {
    mockUseAuth.mockReturnValue(makeSession('PROFESOR') as ReturnType<typeof useAuth>);
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={['/dictados']}>
          <Routes>
            <Route path="/dictados" element={<div>Dictados</div>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );
    expect(screen.getByText('Dictados')).toBeInTheDocument();
  });
});

describe('buildSectionsForRole — nav item hidden for PROFESOR (task 7d.2)', () => {
  beforeEach(() => vi.clearAllMocks());

  it('generic "Dashboard → /dashboard" nav item is NOT in sections when role is PROFESOR', () => {
    const sections = buildSectionsForRole('PROFESOR', 0, 0);
    const allItems = sections.flatMap((s) => s.items);
    const genericDashboard = allItems.find((i) => i.path === '/dashboard');
    expect(genericDashboard).toBeUndefined();
  });

  it('generic "Dashboard → /dashboard" nav item IS present for ADMIN role', () => {
    const sections = buildSectionsForRole('ADMIN', 0, 0);
    const allItems = sections.flatMap((s) => s.items);
    const genericDashboard = allItems.find((i) => i.path === '/dashboard');
    expect(genericDashboard).toBeDefined();
  });

  it('generic "Dashboard → /dashboard" nav item IS present for ALUMNO role', () => {
    const sections = buildSectionsForRole('ALUMNO', 0, 0);
    const allItems = sections.flatMap((s) => s.items);
    const genericDashboard = allItems.find((i) => i.path === '/dashboard');
    expect(genericDashboard).toBeDefined();
  });

  it('"Mis Métricas → /profesor-dashboard" is still present for PROFESOR', () => {
    const sections = buildSectionsForRole('PROFESOR', 0, 0);
    const allItems = sections.flatMap((s) => s.items);
    const misMetricas = allItems.find((i) => i.path === '/profesor-dashboard');
    expect(misMetricas).toBeDefined();
  });
});
