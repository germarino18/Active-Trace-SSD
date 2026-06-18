import * as api from '@/shared/services/api';
import type { TutorAlumno } from '../types/tutor.types';

export async function getTutorAlumnos(): Promise<TutorAlumno[]> {
  return api.get<TutorAlumno[]>('/api/v1/tutor/alumnos');
}
