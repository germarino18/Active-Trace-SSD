import { useMutation } from '@tanstack/react-query';
import * as entregasService from '../services/entregas.service';
import type { EntregasResponse } from '../types';

export function useDetectarEntregas(materiaId: string) {
  return useMutation<EntregasResponse, Error, File>({
    mutationFn: (file) => entregasService.detectarEntregas(materiaId, file),
  });
}

export function useExportarEntregas() {
  return useMutation<void, Error, string>({
    mutationFn: async (materiaId) => {
      const blob = await entregasService.exportarEntregas(materiaId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'entregas-pendientes.csv';
      a.click();
      URL.revokeObjectURL(url);
    },
  });
}
