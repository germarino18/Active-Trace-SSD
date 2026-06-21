/**
 * DashboardEntry — role-aware entry point for the /dashboard route.
 *
 * PROFESOR users are redirected to /profesor-dashboard (their live-metrics page).
 * All other authenticated roles render the generic DashboardPage.
 *
 * Identity is read exclusively from the session (JWT-derived) — never from
 * URL params, body, or any request data (security rule §8).
 */
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { DashboardPage } from '@/pages/DashboardPage';

export function DashboardEntry() {
  const { session } = useAuth();

  if (session.status !== 'authenticated') return null;

  const primaryRole = session.user.roles[0]?.toUpperCase() ?? '';

  if (primaryRole === 'PROFESOR') {
    return <Navigate to="/profesor-dashboard" replace />;
  }

  return <DashboardPage />;
}
