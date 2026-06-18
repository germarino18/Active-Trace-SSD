import * as api from '@/shared/services/api';
import type { ComunicacionPreviewResponse, ComunicacionStatusResponse } from '../types';

export async function getPreview(
  materiaId: string,
  studentIds: string[],
): Promise<ComunicacionPreviewResponse> {
  return api.post<ComunicacionPreviewResponse>(
    `/api/v1/materias/${materiaId}/comunicaciones/preview`,
    { student_ids: studentIds },
  );
}

export async function enviarComunicacion(
  materiaId: string,
  studentIds: string[],
): Promise<{ comunicacion_id: string }> {
  return api.post<{ comunicacion_id: string }>(
    '/api/v1/comunicaciones/enviar',
    { materia_id: materiaId, student_ids: studentIds },
  );
}

export async function getStatus(
  comunicacionId: string,
): Promise<ComunicacionStatusResponse> {
  return api.get<ComunicacionStatusResponse>(
    `/api/v1/comunicaciones/${comunicacionId}/status`,
  );
}
