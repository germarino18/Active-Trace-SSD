import { NavLink } from 'react-router-dom';
import type { MenuItem as MenuItemType } from '@/shared/types';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useSidebar } from './AppLayout';

interface SidebarProps {
  menuItems: MenuItemType[];
}

export function Sidebar({ menuItems }: SidebarProps) {
  const { session, hasAnyPermission } = useAuth();
  const { isOpen, close } = useSidebar();

  const visibleItems = menuItems.filter((item) => {
    if (!item.requiredPermissions || item.requiredPermissions.length === 0) return true;
    return hasAnyPermission(item.requiredPermissions);
  });

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={close}
        />
      )}
      <aside
        className={`fixed left-0 top-0 z-50 flex h-full w-[280px] flex-col border-r border-outline-variant bg-surface-container-lowest px-sm py-md transition-transform duration-300 lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="mb-lg px-xs">
          <div className="flex items-center gap-xs">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-on-primary">
              <span className="material-symbols-outlined">analytics</span>
            </div>
            <div>
              <h1 className="text-headline-md text-sm font-bold text-on-surface">Activia-Trace</h1>
              <p className="text-label-sm text-outline">Academic Management</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1">
          {visibleItems.map((item) => (
            <MenuItem key={item.path} item={item} onClick={close} />
          ))}
        </nav>
        {session.status === 'authenticated' && (
          <div className="mt-auto border-t border-outline-variant px-xs pt-4">
            <div className="flex items-center gap-xs">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/20 text-primary text-label-sm font-bold">
                {session.user.nombre.charAt(0)}{session.user.apellido.charAt(0)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-label-sm font-medium text-on-surface truncate">
                  {session.user.nombre} {session.user.apellido}
                </p>
                <p className="text-label-xs text-outline truncate">{session.user.email}</p>
              </div>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}

interface MenuItemProps {
  item: MenuItemType;
  onClick: () => void;
}

function MenuItem({ item, onClick }: MenuItemProps) {
  return (
    <NavLink
      to={item.path}
      onClick={onClick}
      className={({ isActive }) =>
        `flex items-center gap-sm px-sm py-md rounded-lg text-label-md font-medium transition-colors duration-200 ${
          isActive
            ? 'text-primary bg-surface-container-low border-r-4 border-primary'
            : 'text-on-surface-variant hover:bg-surface-container-low hover:text-on-surface'
        }`
      }
    >
      <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
      <span>{item.label}</span>
    </NavLink>
  );
}
