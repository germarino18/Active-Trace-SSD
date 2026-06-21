import { useQuery } from '@tanstack/react-query';
import * as api from '@/shared/services/api';

export interface RolCatalogo {
  id: string;
  nombre: string;
  descripcion?: string;
}

export function useRoles() {
  return useQuery<RolCatalogo[]>({
    queryKey: ['roles-catalogo'],
    queryFn: () => api.get<RolCatalogo[]>('/api/admin/roles'),
  });
}
