import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { Factura, FacturasResponse, FacturaFilters } from '../types/facturas';
import * as facturasService from '../services/facturas.service';

export function useFacturas(params?: FacturaFilters) {
  return useQuery<FacturasResponse>({
    queryKey: ['facturas', params],
    queryFn: () => facturasService.getFacturas(params),
  });
}

export function useFactura(id: string | undefined) {
  return useQuery<Factura>({
    queryKey: ['facturas', id],
    queryFn: () => facturasService.getFactura(id!),
    enabled: !!id,
  });
}

export function useCrearFactura() {
  const queryClient = useQueryClient();
  return useMutation<Factura, Error, FormData>({
    mutationFn: (data) => facturasService.crearFactura(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] });
    },
  });
}

export function useEditarFactura() {
  const queryClient = useQueryClient();
  return useMutation<Factura, Error, { id: string; data: FormData }>({
    mutationFn: ({ id, data }) => facturasService.editarFactura(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] });
    },
  });
}

export function useCambiarEstadoFactura() {
  const queryClient = useQueryClient();
  return useMutation<Factura, Error, { id: string; estado: 'pendiente' | 'abonada' }>({
    mutationFn: ({ id, estado }) => facturasService.cambiarEstadoFactura(id, estado),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] });
    },
  });
}

export function useEliminarFactura() {
  const queryClient = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (id) => facturasService.eliminarFactura(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['facturas'] });
    },
  });
}
