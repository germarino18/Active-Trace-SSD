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
