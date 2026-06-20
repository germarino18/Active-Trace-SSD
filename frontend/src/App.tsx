import { lazy } from 'react';
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
import { ProfilePage } from '@/pages/ProfilePage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { MateriaLayout } from '@/features/academico/components/MateriaLayout';
import { MateriaListPage } from '@/features/academico/pages/MateriaListPage';
import { ImportarCalificacionesPage } from '@/features/academico/pages/ImportarCalificacionesPage';
import { VistaAtrasadosPage } from '@/features/academico/pages/VistaAtrasadosPage';
import { ComunicacionAtrasadosPage } from '@/features/academico/pages/ComunicacionAtrasadosPage';
import { EntregasSinCorregirPage } from '@/features/academico/pages/EntregasSinCorregirPage';
import { MonitorSeguimientoPage } from '@/features/academico/pages/MonitorSeguimientoPage';
import { AtrasadosGeneralPage } from '@/features/academico/pages/AtrasadosGeneralPage';
import { ComunicacionGeneralPage } from '@/features/academico/pages/ComunicacionGeneralPage';

// Coordinacion pages
const EquiposListPage = lazy(() => import('@/features/coordinacion/pages/EquiposListPage').then(m => ({ default: m.EquiposListPage })));
const MisEquiposPage = lazy(() => import('@/features/coordinacion/pages/MisEquiposPage').then(m => ({ default: m.MisEquiposPage })));
const AsignacionIndividualPage = lazy(() => import('@/features/coordinacion/pages/AsignacionIndividualPage').then(m => ({ default: m.AsignacionIndividualPage })));
const AsignacionMasivaPage = lazy(() => import('@/features/coordinacion/pages/AsignacionMasivaPage').then(m => ({ default: m.AsignacionMasivaPage })));
const ClonarEquipoPage = lazy(() => import('@/features/coordinacion/pages/ClonarEquipoPage').then(m => ({ default: m.ClonarEquipoPage })));
const ModificarVigenciaPage = lazy(() => import('@/features/coordinacion/pages/ModificarVigenciaPage').then(m => ({ default: m.ModificarVigenciaPage })));
const EquipoDetallePage = lazy(() => import('@/features/coordinacion/pages/EquipoDetallePage').then(m => ({ default: m.EquipoDetallePage })));
const AvisosListPage = lazy(() => import('@/features/coordinacion/pages/AvisosListPage').then(m => ({ default: m.AvisosListPage })));
const AvisoCrearPage = lazy(() => import('@/features/coordinacion/pages/AvisoCrearPage').then(m => ({ default: m.AvisoCrearPage })));
const AvisoEditarPage = lazy(() => import('@/features/coordinacion/pages/AvisoEditarPage').then(m => ({ default: m.AvisoEditarPage })));
const TareasListPage = lazy(() => import('@/features/coordinacion/pages/TareasListPage').then(m => ({ default: m.TareasListPage })));
const MisTareasPage = lazy(() => import('@/features/coordinacion/pages/MisTareasPage').then(m => ({ default: m.MisTareasPage })));
const TareaCrearPage = lazy(() => import('@/features/coordinacion/pages/TareaCrearPage').then(m => ({ default: m.TareaCrearPage })));
const TareaDetallePage = lazy(() => import('@/features/coordinacion/pages/TareaDetallePage').then(m => ({ default: m.TareaDetallePage })));
const EncuentrosListPage = lazy(() => import('@/features/coordinacion/pages/EncuentrosListPage').then(m => ({ default: m.EncuentrosListPage })));
const EncuentroCrearPage = lazy(() => import('@/features/coordinacion/pages/EncuentroCrearPage').then(m => ({ default: m.EncuentroCrearPage })));
const EncuentroDetallePage = lazy(() => import('@/features/coordinacion/pages/EncuentroDetallePage').then(m => ({ default: m.EncuentroDetallePage })));
const ConvocatoriasListPage = lazy(() => import('@/features/coordinacion/pages/ConvocatoriasListPage').then(m => ({ default: m.ConvocatoriasListPage })));
const ConvocatoriaCrearPage = lazy(() => import('@/features/coordinacion/pages/ConvocatoriaCrearPage').then(m => ({ default: m.ConvocatoriaCrearPage })));
const ConvocatoriaDetallePage = lazy(() => import('@/features/coordinacion/pages/ConvocatoriaDetallePage').then(m => ({ default: m.ConvocatoriaDetallePage })));
const ProgramasListPage = lazy(() => import('@/features/coordinacion/pages/ProgramasListPage').then(m => ({ default: m.ProgramasListPage })));
const ProgramaCrearPage = lazy(() => import('@/features/coordinacion/pages/ProgramaCrearPage').then(m => ({ default: m.ProgramaCrearPage })));
const FechasAcademicasPage = lazy(() => import('@/features/coordinacion/pages/FechasAcademicasPage').then(m => ({ default: m.FechasAcademicasPage })));
const MonitorGeneralPage = lazy(() => import('@/features/coordinacion/pages/MonitorGeneralPage').then(m => ({ default: m.MonitorGeneralPage })));
const MonitorCoordinacionPage = lazy(() => import('@/features/coordinacion/pages/MonitorCoordinacionPage').then(m => ({ default: m.MonitorCoordinacionPage })));
const AprobacionComunicacionesPage = lazy(() => import('@/features/coordinacion/pages/AprobacionComunicacionesPage').then(m => ({ default: m.AprobacionComunicacionesPage })));

// Finanzas pages
const LiquidacionesPage = lazy(() => import('@/features/finanzas/pages/LiquidacionesPage').then(m => ({ default: m.LiquidacionesPage })));
const GrillaSalarialPage = lazy(() => import('@/features/finanzas/pages/GrillaSalarialPage').then(m => ({ default: m.GrillaSalarialPage })));
const FacturasPage = lazy(() => import('@/features/finanzas/pages/FacturasPage').then(m => ({ default: m.FacturasPage })));

// Admin pages
const EstructuraAcademicaPage = lazy(() => import('@/features/admin/pages/EstructuraAcademicaPage').then(m => ({ default: m.EstructuraAcademicaPage })));
const UsuariosPage = lazy(() => import('@/features/admin/pages/UsuariosPage').then(m => ({ default: m.UsuariosPage })));
const AuditoriaPage = lazy(() => import('@/features/admin/pages/AuditoriaPage').then(m => ({ default: m.AuditoriaPage })));
const MetricasPage = lazy(() => import('@/features/admin/pages/MetricasPage').then(m => ({ default: m.MetricasPage })));

// Nexo pages
const NexoAtrasadosStubPage = lazy(() => import('@/features/nexo/pages/NexoAtrasadosStubPage').then(m => ({ default: m.NexoAtrasadosStubPage })));
const NexoEncuentrosStubPage = lazy(() => import('@/features/nexo/pages/NexoEncuentrosStubPage').then(m => ({ default: m.NexoEncuentrosStubPage })));
const NexoTareasStubPage = lazy(() => import('@/features/nexo/pages/NexoTareasStubPage').then(m => ({ default: m.NexoTareasStubPage })));

// Tutor pages
const TutorAlumnosPage = lazy(() => import('@/features/tutor/pages/TutorAlumnosPage').then(m => ({ default: m.TutorAlumnosPage })));
const GuardiasListPage = lazy(() => import('@/features/tutor/pages/GuardiasListPage').then(m => ({ default: m.GuardiasListPage })));
const TutorEntregasSinCorregirPage = lazy(() => import('@/features/tutor/pages/TutorEntregasSinCorregirPage').then(m => ({ default: m.TutorEntregasSinCorregirPage })));

// Inbox (docentes)
const InboxPage = lazy(() => import('@/features/inbox/pages/InboxPage').then(m => ({ default: m.InboxPage })));
const HiloPage = lazy(() => import('@/features/inbox/pages/HiloPage').then(m => ({ default: m.HiloPage })));

// Alumno pages
const AlumnoDashboardPage = lazy(() => import('@/features/alumno/pages/AlumnoDashboardPage').then(m => ({ default: m.AlumnoDashboardPage })));
const MisMateriasPage = lazy(() => import('@/features/alumno/pages/MisMateriasPage').then(m => ({ default: m.MisMateriasPage })));
const MateriaDetallePage = lazy(() => import('@/features/alumno/pages/MateriaDetallePage').then(m => ({ default: m.MateriaDetallePage })));
const MisColoquiosPage = lazy(() => import('@/features/alumno/pages/MisColoquiosPage').then(m => ({ default: m.MisColoquiosPage })));
const MisAvisosPage = lazy(() => import('@/features/alumno/pages/MisAvisosPage').then(m => ({ default: m.MisAvisosPage })));
const MisProgramasPage = lazy(() => import('@/features/alumno/pages/MisProgramasPage').then(m => ({ default: m.MisProgramasPage })));
const MisFechasPage = lazy(() => import('@/features/alumno/pages/MisFechasPage').then(m => ({ default: m.MisFechasPage })));
const AlumnoInboxPage = lazy(() => import('@/features/alumno/pages/AlumnoInboxPage').then(m => ({ default: m.AlumnoInboxPage })));
const AlumnoHiloPage = lazy(() => import('@/features/alumno/pages/AlumnoHiloPage').then(m => ({ default: m.AlumnoHiloPage })));
const MisComunicacionesPage = lazy(() => import('@/features/alumno/pages/MisComunicacionesPage').then(m => ({ default: m.MisComunicacionesPage })));
const ComunicacionDetallePage = lazy(() => import('@/features/alumno/pages/ComunicacionDetallePage').then(m => ({ default: m.ComunicacionDetallePage })));

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
    element: <Navigate to="/alumno/dashboard" replace />,
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
          { path: '/profile', element: <ProfilePage /> },
          // Tutor
          { path: '/tutor/alumnos', element: <TutorAlumnosPage /> },
          { path: '/entregas-sin-corregir', element: <TutorEntregasSinCorregirPage /> },
          { path: '/guardias', element: <GuardiasListPage /> },
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
          // Atrasados general (cross-materia)
          { path: '/atrasados', element: <AtrasadosGeneralPage /> },
          // Comunicación general (hub por materia)
          { path: '/comunicacion', element: <ComunicacionGeneralPage /> },
          // NEXO stubs
          {
            element: <AuthGuard requiredPermissions={['nexo:atrasados:ver']} />,
            children: [{ path: '/nexo/atrasados', element: <NexoAtrasadosStubPage /> }],
          },
          {
            element: <AuthGuard requiredPermissions={['nexo:encuentros:ver']} />,
            children: [{ path: '/nexo/encuentros', element: <NexoEncuentrosStubPage /> }],
          },
          {
            element: <AuthGuard requiredPermissions={['nexo:tareas:ver']} />,
            children: [{ path: '/nexo/tareas', element: <NexoTareasStubPage /> }],
          },
          // Inbox docentes
          {
            element: <AuthGuard requiredPermissions={['inbox:acceder']} />,
            children: [
              { path: '/inbox', element: <InboxPage /> },
              { path: '/inbox/:id', element: <HiloPage /> },
            ],
          },
          // Equipos Docentes
          { path: '/equipos', element: <EquiposListPage /> },
          { path: '/equipos/mis-equipos', element: <MisEquiposPage /> },
          { path: '/equipos/asignar', element: <AsignacionIndividualPage /> },
          { path: '/equipos/masiva', element: <AsignacionMasivaPage /> },
          { path: '/equipos/clonar', element: <ClonarEquipoPage /> },
          { path: '/equipos/vigencia', element: <ModificarVigenciaPage /> },
          { path: '/equipos/:id', element: <EquipoDetallePage /> },
          // Avisos
          { path: '/avisos', element: <AvisosListPage /> },
          { path: '/avisos/nuevo', element: <AvisoCrearPage /> },
          { path: '/avisos/:id/editar', element: <AvisoEditarPage /> },
          // Tareas
          { path: '/tareas', element: <TareasListPage /> },
          { path: '/tareas/mias', element: <MisTareasPage /> },
          { path: '/tareas/nueva', element: <TareaCrearPage /> },
          { path: '/tareas/:id', element: <TareaDetallePage /> },
          // Encuentros
          { path: '/encuentros', element: <EncuentrosListPage /> },
          { path: '/encuentros/nuevo', element: <EncuentroCrearPage /> },
          { path: '/encuentros/:id', element: <EncuentroDetallePage /> },
          // Coloquios
          { path: '/coloquios', element: <ConvocatoriasListPage /> },
          { path: '/coloquios/nuevo', element: <ConvocatoriaCrearPage /> },
          { path: '/coloquios/:id', element: <ConvocatoriaDetallePage /> },
          // Programas
          { path: '/programas', element: <ProgramasListPage /> },
          { path: '/programas/nuevo', element: <ProgramaCrearPage /> },
          { path: '/fechas', element: <FechasAcademicasPage /> },
          // Aprobación de comunicaciones
          {
            element: <AuthGuard requiredPermissions={['comunicacion:aprobar']} />,
            children: [
              { path: '/comunicaciones/aprobar', element: <AprobacionComunicacionesPage /> },
            ],
          },
          // Monitores
          { path: '/monitores/general', element: <MonitorGeneralPage /> },
          { path: '/monitores/coordinacion', element: <MonitorCoordinacionPage /> },
          // Finanzas
          { path: '/finanzas/liquidaciones', element: <LiquidacionesPage /> },
          { path: '/finanzas/grilla', element: <GrillaSalarialPage /> },
          { path: '/finanzas/facturas', element: <FacturasPage /> },
          // Admin
          { path: '/admin/estructura', element: <EstructuraAcademicaPage /> },
          { path: '/admin/usuarios', element: <UsuariosPage /> },
          { path: '/admin/auditoria', element: <AuditoriaPage /> },
          { path: '/admin/metricas', element: <MetricasPage /> },
          // Alumno
          { path: '/alumno/dashboard', element: <AlumnoDashboardPage /> },
          { path: '/alumno/materias', element: <MisMateriasPage /> },
          { path: '/alumno/materias/:id', element: <MateriaDetallePage /> },
          { path: '/alumno/coloquios', element: <MisColoquiosPage /> },
          { path: '/alumno/avisos', element: <MisAvisosPage /> },
          { path: '/alumno/programas', element: <MisProgramasPage /> },
          { path: '/alumno/fechas', element: <MisFechasPage /> },
          { path: '/alumno/inbox', element: <AlumnoInboxPage /> },
          { path: '/alumno/inbox/:id', element: <AlumnoHiloPage /> },
          { path: '/alumno/comunicaciones', element: <MisComunicacionesPage /> },
          { path: '/alumno/comunicaciones/:id', element: <ComunicacionDetallePage /> },
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
