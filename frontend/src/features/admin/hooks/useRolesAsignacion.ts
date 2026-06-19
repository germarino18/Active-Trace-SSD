import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as rolesService from '../services/roles.service';

export function useRolesAsignacion(usuarioId: string | undefined) {
  return useQuery({
    queryKey: ['usuarios-roles', usuarioId],
    queryFn: () => rolesService.getRolesUsuario(usuarioId!),
    enabled: !!usuarioId,
  });
}

export function useAsignarRolUsuario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ usuarioId, rol_id }: { usuarioId: string; rol_id: string }) =>
      rolesService.asignarRolUsuario(usuarioId, { rol_id }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['usuarios-roles', variables.usuarioId] });
    },
  });
}

export function useRemoverRolUsuario() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ usuarioId, rolId }: { usuarioId: string; rolId: string }) =>
      rolesService.removerRolUsuario(usuarioId, rolId),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['usuarios-roles', variables.usuarioId] });
    },
  });
}
