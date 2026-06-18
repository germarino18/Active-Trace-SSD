import * as api from '@/shared/services/api';
import type { EntregasResponse } from '../types';

export async function detectarEntregas(
  materiaId: string,
  file: File,
): Promise<EntregasResponse> {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<EntregasResponse>(
    `/api/v1/materias/${materiaId}/detectar-entregas`,
    formData,
  );
}

export async function exportarEntregas(materiaId: string): Promise<Blob> {
  const response = await fetch(`/api/v1/materias/${materiaId}/entregas-pendientes/export`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token') ?? ''}`,
    },
  });
  if (!response.ok) {
    throw new Error('Error al exportar entregas');
  }
  return response.blob();
}
