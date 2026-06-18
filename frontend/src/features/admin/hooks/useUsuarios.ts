import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { Usuario, UsuariosResponse, CrearUsuarioData, EditarUsuarioData } from '../types';
import type { UsuarioFilters } from '../types/usuarios';
import * as usuariosService from '../services/usuarios.service';

export function useUsuarios(params?: UsuarioFilters) {
  return useQuery<UsuariosResponse>({
    queryKey: ['usuarios', params],
    queryFn: () => usuariosService.getUsuarios(params),
  });
}

export function useUsuario(id: string | undefined) {
  return useQuery<Usuario>({
    queryKey: ['usuarios', id],
    queryFn: () => usuariosService.getUsuario(id!),
    enabled: !!id,
  });
}

export function useCrearUsuario() {
  const queryClient = useQueryClient();
  return useMutation<Usuario, Error, CrearUsuarioData>({
    mutationFn: (data) => usuariosService.crearUsuario(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });
}

export function useEditarUsuario() {
  const queryClient = useQueryClient();
  return useMutation<Usuario, Error, { id: string; data: EditarUsuarioData }>({
    mutationFn: ({ id, data }) => usuariosService.editarUsuario(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] });
    },
  });
}
