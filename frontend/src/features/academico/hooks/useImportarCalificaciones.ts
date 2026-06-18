import { useMutation } from '@tanstack/react-query';
import * as importarService from '../services/importar.service';
import type { ImportPreviewResponse } from '../types';

export function useUploadCalificaciones(materiaId: string) {
  return useMutation<ImportPreviewResponse, Error, File>({
    mutationFn: (file) => importarService.uploadCalificaciones(file, materiaId),
  });
}

export function useConfirmarImportacion(materiaId: string) {
  return useMutation<{ message: string }, Error, string[]>({
    mutationFn: (activityIds) => importarService.confirmarImportacion(materiaId, activityIds),
  });
}

export function useConfigurarUmbral(materiaId: string) {
  return useMutation<{ message: string }, Error, number>({
    mutationFn: (porcentaje) => importarService.configurarUmbral(materiaId, porcentaje),
  });
}
