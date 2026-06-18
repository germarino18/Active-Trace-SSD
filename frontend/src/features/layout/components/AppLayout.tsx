import { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Breadcrumbs } from './Breadcrumbs';
import type { MenuItem } from '@/shared/types';
import { useAuth } from '@/features/auth/hooks/useAuth';

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

const defaultMenuItems: MenuItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
  { label: 'Calificaciones', path: '/materias', icon: 'grading', requiredPermissions: ['calificaciones:*'] },
  { label: 'Atrasados', path: '/materias', icon: 'warning', requiredPermissions: ['atrasados:*'] },
  { label: 'Comunicación', path: '/materias', icon: 'send', requiredPermissions: ['comunicacion:*'] },
  { label: 'Mi Perfil', path: '/profile', icon: 'person' },
  // Alumno
  { label: 'Dashboard', path: '/alumno/dashboard', icon: 'dashboard', requiredPermissions: ['estado-academico:ver'] },
  { label: 'Mis Materias', path: '/alumno/materias', icon: 'school', requiredPermissions: ['estado-academico:ver'] },
  { label: 'Coloquios', path: '/alumno/coloquios', icon: 'quiz', requiredPermissions: ['evaluacion:reservar'] },
  { label: 'Avisos', path: '/alumno/avisos', icon: 'campaign', requiredPermissions: ['avisos:confirmar'] },
  { label: 'Programas', path: '/alumno/programas', icon: 'description', requiredPermissions: ['estado-academico:ver'] },
  { label: 'Calendario', path: '/alumno/fechas', icon: 'calendar_month', requiredPermissions: ['estado-academico:ver'] },
  { label: 'Mensajes', path: '/alumno/inbox', icon: 'mail', requiredPermissions: ['inbox:ver'] },
  { label: 'Comunicaciones', path: '/alumno/comunicaciones', icon: 'forward_to_inbox', requiredPermissions: ['comunicacion:ver'] },
  { label: 'Equipos Docentes', path: '/equipos', icon: 'groups', requiredPermissions: ['equipos:*'] },
  { label: 'Avisos', path: '/avisos', icon: 'campaign', requiredPermissions: ['avisos:*'] },
  { label: 'Tareas', path: '/tareas', icon: 'checklist', requiredPermissions: ['tareas:*'] },
  { label: 'Encuentros', path: '/encuentros', icon: 'event', requiredPermissions: ['encuentros:*'] },
  { label: 'Coloquios', path: '/coloquios', icon: 'quiz', requiredPermissions: ['coloquios:*'] },
  { label: 'Programas', path: '/programas', icon: 'description', requiredPermissions: ['programas:*'] },
  { label: 'Fechas Académicas', path: '/fechas', icon: 'calendar_month', requiredPermissions: ['programas:*'] },
  { label: 'Monitores', path: '/monitores/general', icon: 'monitoring', requiredPermissions: ['auditoria:*'] },
  // Finanzas
  { label: 'Liquidaciones', path: '/finanzas/liquidaciones', icon: 'payments', requiredPermissions: ['liquidaciones:*'] },
  { label: 'Grilla Salarial', path: '/finanzas/grilla', icon: 'badge', requiredPermissions: ['liquidaciones:configurar-salarios'] },
  { label: 'Facturas', path: '/finanzas/facturas', icon: 'receipt_long', requiredPermissions: ['facturas:*'] },
  // Admin
  { label: 'Estructura Académica', path: '/admin/estructura', icon: 'account_tree', requiredPermissions: ['estructura:*'] },
  { label: 'Usuarios', path: '/admin/usuarios', icon: 'manage_accounts', requiredPermissions: ['usuarios:*'] },
  { label: 'Auditoría', path: '/admin/auditoria', icon: 'summarize', requiredPermissions: ['auditoria:*'] },
  { label: 'Métricas', path: '/admin/metricas', icon: 'monitoring', requiredPermissions: ['auditoria:*'] },
];

export function AppLayout() {
  const { session } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

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
        <Sidebar menuItems={defaultMenuItems} />
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
