import { useMutation, useQueryClient } from '@tanstack/react-query';
import { responder } from '../services/inbox.service';
import type { ResponderPayload } from '../types/inbox.types';
import { INBOX_HILOS_QUERY_KEY } from './useInbox';

export function useResponder(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ResponderPayload) => responder(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inbox', 'hilo', id] });
      queryClient.invalidateQueries({ queryKey: INBOX_HILOS_QUERY_KEY });
    },
  });
}
