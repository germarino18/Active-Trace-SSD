import { useQuery } from '@tanstack/react-query';
import * as tutorEntregasService from '../services/entregas.service';
import type { EntregasResponse } from '@/features/academico/types';

export function useTutorEntregas() {
  return useQuery<EntregasResponse>({
    queryKey: ['tutor', 'entregas-sin-corregir'],
    queryFn: () => tutorEntregasService.getEntregasSinCorregir(),
  });
}
