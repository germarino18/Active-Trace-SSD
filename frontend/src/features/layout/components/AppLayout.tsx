import { createContext, useContext, useState, useCallback, useMemo } from 'react';
import type { ReactNode } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Breadcrumbs } from './Breadcrumbs';
import type { SidebarSection } from '@/shared/types';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useLotesPendientesCount } from '@/features/coordinacion/hooks/useAprobacionComunicaciones';

interface SidebarContextValue {
  isOpen: boolean;
  toggle: () => void;
  close: () => void;
}

const SidebarContext = createContext<SidebarContextValue>({
  isOpen: false,
  toggle: () => {},
  close: () => {},
});

export function useSidebar() {
  return useContext(SidebarContext);
}

function buildSections(comunicacionesPendientes: number): SidebarSection[] {
  return [
    // Items visibles para todos los usuarios autenticados
    {
      items: [
        { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
        { label: 'Mi Perfil', path: '/profile', icon: 'person' },
      ],
    },
    // ALUMNO
    {
      label: 'ALUMNO',
      items: [
        { label: 'Dashboard', path: '/alumno/dashboard', icon: 'dashboard', requiredPermissions: ['estado-academico:ver'] },
        { label: 'Mis Materias', path: '/alumno/materias', icon: 'school', requiredPermissions: ['estado-academico:ver'] },
        { label: 'Coloquios', path: '/alumno/coloquios', icon: 'quiz', requiredPermissions: ['evaluacion:reservar'] },
        { label: 'Avisos', path: '/alumno/avisos', icon: 'campaign', requiredPermissions: ['avisos:confirmar'] },
        { label: 'Programas', path: '/alumno/programas', icon: 'description', requiredPermissions: ['estado-academico:ver'] },
        { label: 'Calendario', path: '/alumno/fechas', icon: 'calendar_month', requiredPermissions: ['estado-academico:ver'] },
        { label: 'Mensajes', path: '/alumno/inbox', icon: 'mail', requiredPermissions: ['inbox:ver'] },
        { label: 'Comunicaciones', path: '/alumno/comunicaciones', icon: 'forward_to_inbox', requiredPermissions: ['comunicacion:ver'] },
      ],
    },
    // Docente (TUTOR / PROFESOR)
    {
      label: 'Docente',
      items: [
        { label: 'Calificaciones', path: '/materias', icon: 'grading', requiredPermissions: ['calificaciones:ver'] },
        { label: 'Mis Alumnos', path: '/tutor/alumnos', icon: 'group', requiredPermissions: ['alumnos:ver'] },
        { label: 'Entregas sin corregir', path: '/entregas-sin-corregir', icon: 'assignment_late', requiredPermissions: ['entregas:ver'] },
        { label: 'Guardias', path: '/guardias', icon: 'shield', requiredPermissions: ['guardias:gestionar'] },
        { label: 'Atrasados', path: '/atrasados', icon: 'warning', requiredPermissions: ['atrasados:ver'] },
        { label: 'Comunicación', path: '/comunicacion', icon: 'send', requiredPermissions: ['comunicacion:ver'] },
        { label: 'Encuentros', path: '/encuentros', icon: 'event', requiredPermissions: ['encuentros:gestionar'] },
        { label: 'Coloquios', path: '/coloquios', icon: 'quiz', requiredPermissions: ['coloquios:gestionar'] },
      ],
    },
    // NEXO — solo lectura por carrera
    {
      label: 'NEXO',
      items: [
        { label: 'Atrasados', path: '/nexo/atrasados', icon: 'warning', requiredPermissions: ['nexo:atrasados:ver'] },
        { label: 'Encuentros', path: '/nexo/encuentros', icon: 'event', requiredPermissions: ['nexo:encuentros:ver'] },
        { label: 'Tareas', path: '/nexo/tareas', icon: 'checklist', requiredPermissions: ['nexo:tareas:ver'] },
      ],
    },
    // Coordinación
    {
      label: 'Coordinación',
      items: [
        { label: 'Equipos Docentes', path: '/equipos', icon: 'groups', requiredPermissions: ['equipos:ver'] },
        { label: 'Avisos', path: '/avisos', icon: 'campaign', requiredPermissions: ['avisos:ver'] },
        { label: 'Tareas', path: '/tareas', icon: 'checklist', requiredPermissions: ['tareas:ver'] },
        { label: 'Programas', path: '/programas', icon: 'description', requiredPermissions: ['programas:ver'] },
        { label: 'Fechas Académicas', path: '/fechas', icon: 'calendar_month', requiredPermissions: ['programas:ver'] },
        { label: 'Monitores', path: '/monitores/general', icon: 'monitoring', requiredPermissions: ['auditoria:ver'] },
        {
          label: 'Aprobar Comunicaciones',
          path: '/comunicaciones/aprobar',
          icon: 'approval',
          requiredPermissions: ['comunicacion:aprobar'],
          badge: comunicacionesPendientes,
        },
      ],
    },
    // Finanzas
    {
      label: 'Finanzas',
      items: [
        { label: 'Liquidaciones', path: '/finanzas/liquidaciones', icon: 'payments', requiredPermissions: ['liquidaciones:ver'] },
        { label: 'Grilla Salarial', path: '/finanzas/grilla', icon: 'badge', requiredPermissions: ['liquidaciones:configurar-salarios'] },
        { label: 'Facturas', path: '/finanzas/facturas', icon: 'receipt_long', requiredPermissions: ['facturas:ver'] },
      ],
    },
    // Admin
    {
      label: 'Admin',
      items: [
        { label: 'Estructura Académica', path: '/admin/estructura', icon: 'account_tree', requiredPermissions: ['estructura:ver'] },
        { label: 'Usuarios', path: '/admin/usuarios', icon: 'manage_accounts', requiredPermissions: ['usuarios:ver'] },
        { label: 'Auditoría', path: '/admin/auditoria', icon: 'summarize', requiredPermissions: ['auditoria:ver'] },
        { label: 'Métricas', path: '/admin/metricas', icon: 'monitoring', requiredPermissions: ['auditoria:ver'] },
      ],
    },
  ];
}

export function AppLayout() {
  const { session } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const pendingCount = useLotesPendientesCount();
  const sections = useMemo(() => buildSections(pendingCount), [pendingCount]);

  const toggle = useCallback(() => setIsOpen((prev) => !prev), []);
  const close = useCallback(() => setIsOpen(false), []);

  if (session.status === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="h-10 w-10 animate-spin rounded-full border-2 border-outline-variant border-t-primary" role="status" />
      </div>
    );
  }

  return (
    <SidebarContext.Provider value={{ isOpen, toggle, close }}>
      <div className="flex min-h-screen bg-background">
        <Sidebar sections={sections} />
        <div className="flex flex-1 flex-col">
          <Header breadcrumbs={[{ label: 'Inicio', path: '/dashboard' }]} />
          <main className="flex-1 p-gutter custom-scrollbar">
            <div className="mb-4">
              <Breadcrumbs />
            </div>
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarContext.Provider>
  );
}
