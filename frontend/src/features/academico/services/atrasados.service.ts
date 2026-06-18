import * as api from '@/shared/services/api';
import type { AtrasadosResponse, RankingResponse, NotasFinalesResponse, ReportesRapidosResponse } from '../types';

export async function getAtrasados(materiaId: string): Promise<AtrasadosResponse> {
  return api.get<AtrasadosResponse>(`/api/v1/materias/${materiaId}/atrasados`);
}

export async function getRanking(materiaId: string): Promise<RankingResponse> {
  return api.get<RankingResponse>(`/api/v1/materias/${materiaId}/ranking`);
}

export async function getNotasFinales(materiaId: string): Promise<NotasFinalesResponse> {
  return api.get<NotasFinalesResponse>(`/api/v1/materias/${materiaId}/notas-finales`);
}

export async function getReportesRapidos(materiaId: string): Promise<ReportesRapidosResponse> {
  return api.get<ReportesRapidosResponse>(`/api/v1/materias/${materiaId}/reportes-rapidos`);
}
