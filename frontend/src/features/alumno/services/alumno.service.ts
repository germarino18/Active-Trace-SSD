import * as api from '@/shared/services/api';
import type {
  AlumnoDashboardResponse,
  AvisoAlumno,
  ComunicacionDetalle,
  ComunicacionRecibida,
  ConvocatoriaColoquio,
  EstadoAcademicoMateria,
  FechaAcademica,
  HiloInbox,
  MensajeHilo,
  ProgramaMateria,
  ReservaColoquio,
} from '../types/alumno.types';

export async function getDashboard(): Promise<AlumnoDashboardResponse> {
  return api.get<AlumnoDashboardResponse>('/api/v1/alumno/dashboard');
}

export async function getMaterias(): Promise<EstadoAcademicoMateria[]> {
  return api.get<EstadoAcademicoMateria[]>('/api/v1/alumno/materias');
}

export async function getMateriaDetalle(
  id: string,
): Promise<EstadoAcademicoMateria> {
  return api.get<EstadoAcademicoMateria>(`/api/v1/alumno/materias/${id}`);
}

export async function getConvocatorias(): Promise<ConvocatoriaColoquio[]> {
  return api.get<ConvocatoriaColoquio[]>('/api/v1/coloquios');
}

export async function reservarTurno(
  convocatoriaId: string,
): Promise<ReservaColoquio> {
  return api.post<ReservaColoquio>(
    `/api/v1/coloquios/${convocatoriaId}/reservar`,
  );
}

export async function cancelarReserva(
  reservaId: string,
): Promise<ReservaColoquio> {
  return api.post<ReservaColoquio>(
    `/api/v1/coloquios/reservas/${reservaId}/cancelar`,
  );
}

export async function getAvisos(): Promise<AvisoAlumno[]> {
  return api.get<AvisoAlumno[]>('/api/v1/avisos/visible');
}

export async function confirmarAviso(avisoId: string): Promise<void> {
  return api.post<void>(`/api/v1/avisos/${avisoId}/confirmar`);
}

export async function getProgramas(): Promise<ProgramaMateria[]> {
  return api.get<ProgramaMateria[]>('/api/v1/alumno/programas');
}

export async function getFechas(): Promise<FechaAcademica[]> {
  return api.get<FechaAcademica[]>('/api/v1/alumno/fechas');
}

export async function getHilos(): Promise<HiloInbox[]> {
  return api.get<HiloInbox[]>('/api/v1/inbox/hilos');
}

export async function getHilo(hiloId: string): Promise<MensajeHilo[]> {
  return api.get<MensajeHilo[]>(`/api/v1/inbox/hilos/${hiloId}`);
}

export async function responderHilo(
  hiloId: string,
  contenido: string,
): Promise<MensajeHilo> {
  return api.post<MensajeHilo>(
    `/api/v1/inbox/hilos/${hiloId}/responder`,
    { contenido },
  );
}

export async function getComunicaciones(): Promise<ComunicacionRecibida[]> {
  return api.get<ComunicacionRecibida[]>('/api/v1/alumno/comunicaciones');
}

export async function getComunicacionDetalle(
  comunicacionId: string,
): Promise<ComunicacionDetalle> {
  return api.get<ComunicacionDetalle>(
    `/api/v1/alumno/comunicaciones/${comunicacionId}`,
  );
}
