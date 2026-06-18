import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Spinner } from '@/shared/components/Spinner';

interface AuthGuardProps {
  requiredPermissions?: string[];
  children?: React.ReactNode;
}

export function AuthGuard({ requiredPermissions, children }: AuthGuardProps) {
  const { session, hasAnyPermission } = useAuth();
  const location = useLocation();

  if (session.status === 'loading') {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background">
        <Spinner />
      </div>
    );
  }

  if (session.status === 'unauthenticated') {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredPermissions && requiredPermissions.length > 0) {
    if (!hasAnyPermission(requiredPermissions)) {
      return <Navigate to="/forbidden" replace />;
    }
  }

  return children ? <>{children}</> : <Outlet />;
}
