import type { ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { ForbiddenPage } from '@/pages/ForbiddenPage';

interface PermissionGuardProps {
  permissions: string[];
  children: ReactNode;
}

export function PermissionGuard({ permissions, children }: PermissionGuardProps) {
  const { hasAnyPermission } = useAuth();

  if (!hasAnyPermission(permissions)) {
    return <ForbiddenPage />;
  }

  return <>{children}</>;
}
