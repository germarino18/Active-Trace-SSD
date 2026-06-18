import * as api from '@/shared/services/api';
import type { Tarea, TareasResponse, ComentarioTarea } from '../types';

export interface TareaParams {
  asignado_id?: string;
  asignado_por_id?: string;
  materia_id?: string;
  estado?: string;
  q?: string;
  offset?: number;
  limit?: number;
}

export interface CrearTareaData {
  titulo: string;
  descripcion: string;
  asignado_id: string;
  materia_id?: string;
  cohorte_id?: string;
}

export async function getMisTareas(params?: TareaParams): Promise<TareasResponse> {
  return api.get<TareasResponse>('/api/v1/tareas/mias', params as Record<string, unknown>);
}

export async function getTareas(params?: TareaParams): Promise<TareasResponse> {
  return api.get<TareasResponse>('/api/v1/tareas', params as Record<string, unknown>);
}

export async function getTarea(id: string): Promise<Tarea> {
  return api.get<Tarea>(`/api/v1/tareas/${id}`);
}

export async function crearTarea(data: CrearTareaData): Promise<Tarea> {
  return api.post<Tarea>('/api/v1/tareas', data);
}

export async function cambiarEstado(tareaId: string, estado: string, razon?: string): Promise<Tarea> {
  return api.patch<Tarea>(`/api/v1/tareas/${tareaId}/estado`, { estado, razon_cancelacion: razon });
}

export async function agregarComentario(tareaId: string, contenido: string): Promise<ComentarioTarea> {
  return api.post<ComentarioTarea>(`/api/v1/tareas/${tareaId}/comentarios`, { contenido });
}

export async function delegarTarea(tareaId: string, nuevoAsignadoId: string): Promise<Tarea> {
  return api.patch<Tarea>(`/api/v1/tareas/${tareaId}/delegar`, { nuevo_asignado_id: nuevoAsignadoId });
}
