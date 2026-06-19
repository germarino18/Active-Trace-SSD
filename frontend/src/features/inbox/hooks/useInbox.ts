import { useQuery } from '@tanstack/react-query';
import { getHilos } from '../services/inbox.service';

export const INBOX_HILOS_QUERY_KEY = ['inbox', 'hilos'] as const;

export function useInbox() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: INBOX_HILOS_QUERY_KEY,
    queryFn: getHilos,
    staleTime: 30_000,
  });

  const hilos = data ?? [];
  const unreadCount = hilos.filter((h) => !h.leido).length;

  return { hilos, unreadCount, isLoading, error, refetch };
}
