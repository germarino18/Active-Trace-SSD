import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/features/auth/context/AuthContext';
import { AuthGuard } from '@/features/auth/components/AuthGuard';
import { GuestGuard } from '@/features/auth/components/GuestGuard';
import { LoginPage } from '@/features/auth/pages/LoginPage';
import { TwoFactorPage } from '@/features/auth/pages/TwoFactorPage';
import { ForgotPasswordPage } from '@/features/auth/pages/ForgotPasswordPage';
import { ResetPasswordPage } from '@/features/auth/pages/ResetPasswordPage';
import { AppLayout } from '@/features/layout/components/AppLayout';
import { DashboardPage } from '@/pages/DashboardPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { MateriaLayout } from '@/features/academico/components/MateriaLayout';
import { MateriaListPage } from '@/features/academico/pages/MateriaListPage';
import { ImportarCalificacionesPage } from '@/features/academico/pages/ImportarCalificacionesPage';
import { VistaAtrasadosPage } from '@/features/academico/pages/VistaAtrasadosPage';
import { ComunicacionAtrasadosPage } from '@/features/academico/pages/ComunicacionAtrasadosPage';
import { EntregasSinCorregirPage } from '@/features/academico/pages/EntregasSinCorregirPage';
import { MonitorSeguimientoPage } from '@/features/academico/pages/MonitorSeguimientoPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    element: <GuestGuard />,
    children: [
      { path: '/login', element: <LoginPage /> },
      { path: '/2fa', element: <TwoFactorPage /> },
      { path: '/forgot-password', element: <ForgotPasswordPage /> },
      { path: '/reset-password', element: <ResetPasswordPage /> },
    ],
  },
  {
    element: <AuthGuard />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/profile', element: <ProfilePage /> },
          { path: '/materias', element: <MateriaListPage /> },
          {
            path: '/materias/:id',
            element: <MateriaLayout />,
            children: [
              { index: true, element: <Navigate to="importar" replace /> },
              { path: 'importar', element: <ImportarCalificacionesPage /> },
              { path: 'atrasados', element: <VistaAtrasadosPage /> },
              { path: 'comunicar', element: <ComunicacionAtrasadosPage /> },
              { path: 'entregas-pendientes', element: <EntregasSinCorregirPage /> },
              { path: 'monitor', element: <MonitorSeguimientoPage /> },
            ],
          },
        ],
      },
    ],
  },
  {
    path: '/forbidden',
    lazy: () => import('@/pages/ForbiddenPage').then((m) => ({ Component: m.ForbiddenPage })),
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  );
}
