import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useSidebar } from './AppLayout';

interface HeaderProps {
  breadcrumbs?: Array<{ label: string; path: string }>;
}

export function Header({ breadcrumbs }: HeaderProps) {
  const { session, logout } = useAuth();
  const { toggle } = useSidebar();
  const navigate = useNavigate();
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    setUserMenuOpen(false);
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-outline-variant bg-background/80 px-gutter backdrop-blur-md">
      <div className="flex items-center gap-md">
        <button
          onClick={toggle}
          className="text-on-surface-variant hover:text-primary transition-colors md:hidden"
          aria-label="Toggle sidebar"
        >
          <span className="material-symbols-outlined">menu</span>
        </button>
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="hidden sm:flex items-center gap-2 text-label-sm text-on-surface-variant">
            {breadcrumbs.map((crumb, index) => (
              <span key={crumb.path} className="flex items-center gap-2">
                {index > 0 && <span className="text-outline">/</span>}
                {index < breadcrumbs.length - 1 ? (
                  <Link to={crumb.path} className="hover:text-primary transition-colors">
                    {crumb.label}
                  </Link>
                ) : (
                  <span className="text-on-surface">{crumb.label}</span>
                )}
              </span>
            ))}
          </nav>
        )}
      </div>
      <div className="flex items-center gap-md">
        <button className="relative text-on-surface-variant hover:text-primary transition-colors">
          <span className="material-symbols-outlined">notifications</span>
          <span className="absolute right-0 top-0 h-2 w-2 rounded-full border-2 border-surface-container-lowest bg-error" />
        </button>
        {session.status === 'authenticated' && (
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center gap-sm border-l border-outline-variant pl-md transition-colors hover:text-primary"
            >
              <div className="hidden text-right lg:block">
                <p className="text-label-sm font-bold text-on-surface">
                  {session.user.nombre} {session.user.apellido}
                </p>
                <p className="text-label-xs text-outline">{session.user.email}</p>
              </div>
              <div className="flex h-10 w-10 items-center justify-center rounded-full border border-outline-variant bg-primary/20 text-primary text-label-sm font-bold">
                {session.user.nombre.charAt(0)}{session.user.apellido.charAt(0)}
              </div>
            </button>
            {userMenuOpen && (
              <div className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-outline-variant bg-surface-container-lowest p-2 shadow-lg">
                <div className="px-3 py-2 border-b border-outline-variant mb-1">
                  <p className="text-label-sm font-medium text-on-surface">
                    {session.user.nombre} {session.user.apellido}
                  </p>
                  <p className="text-label-xs text-outline">{session.user.email}</p>
                </div>
                <Link
                  to="/profile"
                  onClick={() => setUserMenuOpen(false)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg text-label-sm text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
                >
                  <span className="material-symbols-outlined text-[18px]">person</span>
                  Mi Perfil
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 px-3 py-2 rounded-lg text-label-sm text-error hover:bg-error-container transition-colors"
                >
                  <span className="material-symbols-outlined text-[18px]">logout</span>
                  Cerrar sesión
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
