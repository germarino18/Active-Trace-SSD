import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getHilo } from '../services/inbox.service';
import { INBOX_HILOS_QUERY_KEY } from './useInbox';

export function useHilo(id: string) {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['inbox', 'hilo', id],
    queryFn: async () => {
      const result = await getHilo(id);
      // getHilo marca el hilo como leído en backend, así que refrescamos la lista
      queryClient.invalidateQueries({ queryKey: INBOX_HILOS_QUERY_KEY });
      return result;
    },
    enabled: !!id,
  });

  return { mensajes: data ?? [], isLoading, error };
}
