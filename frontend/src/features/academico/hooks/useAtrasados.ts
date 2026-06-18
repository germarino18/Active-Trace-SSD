import { useQuery } from '@tanstack/react-query';
import * as atrasadosService from '../services/atrasados.service';
import type { AtrasadosResponse, RankingResponse, NotasFinalesResponse, ReportesRapidosResponse } from '../types';

export function useAtrasados(materiaId: string) {
  return useQuery<AtrasadosResponse>({
    queryKey: ['atrasados', materiaId],
    queryFn: () => atrasadosService.getAtrasados(materiaId),
    enabled: !!materiaId,
  });
}

export function useRanking(materiaId: string) {
  return useQuery<RankingResponse>({
    queryKey: ['ranking', materiaId],
    queryFn: () => atrasadosService.getRanking(materiaId),
    enabled: !!materiaId,
  });
}

export function useNotasFinales(materiaId: string) {
  return useQuery<NotasFinalesResponse>({
    queryKey: ['notas-finales', materiaId],
    queryFn: () => atrasadosService.getNotasFinales(materiaId),
    enabled: !!materiaId,
  });
}

export function useReportesRapidos(materiaId: string) {
  return useQuery<ReportesRapidosResponse>({
    queryKey: ['reportes-rapidos', materiaId],
    queryFn: () => atrasadosService.getReportesRapidos(materiaId),
    enabled: !!materiaId,
  });
}
