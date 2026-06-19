import { useQuery } from '@tanstack/react-query';
import { getHilo } from '../services/inbox.service';

export function useHilo(id: string) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['inbox', 'hilo', id],
    queryFn: () => getHilo(id),
    enabled: !!id,
  });

  return { mensajes: data ?? [], isLoading, error };
}
