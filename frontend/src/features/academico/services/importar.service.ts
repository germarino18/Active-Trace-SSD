import * as api from '@/shared/services/api';
import type { ImportPreviewResponse } from '../types';

export async function uploadCalificaciones(
  file: File,
  materiaId: string,
): Promise<ImportPreviewResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<ImportPreviewResponse>(
    `/api/v1/materias/${materiaId}/importar-calificaciones`,
    formData,
  );
  return response;
}

export async function confirmarImportacion(
  materiaId: string,
  activityIds: string[],
): Promise<{ message: string }> {
  return api.post<{ message: string }>(
    `/api/v1/materias/${materiaId}/importar-calificaciones`,
    { activity_ids: activityIds },
  );
}

export async function configurarUmbral(
  materiaId: string,
  porcentaje: number,
): Promise<{ message: string }> {
  return api.post<{ message: string }>(
    `/api/v1/materias/${materiaId}/configurar-umbral`,
    { porcentaje },
  );
}
