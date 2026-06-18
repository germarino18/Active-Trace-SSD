import { useQuery } from '@tanstack/react-query';
import * as tutorService from '../services/tutor.service';
import type { TutorAlumno } from '../types/tutor.types';

export function useTutorAlumnos() {
  return useQuery<TutorAlumno[]>({
    queryKey: ['tutor', 'alumnos'],
    queryFn: () => tutorService.getTutorAlumnos(),
  });
}
