import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as api from '@/shared/services/api';
import type { ProfilePatchRequest, ProfileResponse } from '../types';

const PROFILE_KEY = ['perfil'] as const;

export function useProfileQuery() {
  return useQuery<ProfileResponse>({
    queryKey: PROFILE_KEY,
    queryFn: () => api.get<ProfileResponse>('/api/v1/perfil'),
  });
}

export function useProfileMutation() {
  const queryClient = useQueryClient();

  return useMutation<ProfileResponse, Error, ProfilePatchRequest>({
    mutationFn: (data) => api.patch<ProfileResponse>('/api/v1/perfil', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: PROFILE_KEY });
    },
  });
}
