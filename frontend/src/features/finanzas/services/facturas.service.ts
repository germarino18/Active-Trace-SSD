import * as api from '@/shared/services/api';
import apiClient from '@/shared/services/api';
import type { Factura, FacturasResponse, FacturaFilters } from '../types/facturas';

export async function getFacturas(params?: FacturaFilters): Promise<FacturasResponse> {
  return api.get<FacturasResponse>('/api/v1/facturas', params as Record<string, unknown>);
}

export async function getFactura(id: string): Promise<Factura> {
  return api.get<Factura>(`/api/v1/facturas/${id}`);
}

export async function crearFactura(data: FormData): Promise<Factura> {
  const response = await apiClient.post<Factura>('/api/v1/facturas', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function editarFactura(id: string, data: FormData): Promise<Factura> {
  const response = await apiClient.put<Factura>(`/api/v1/facturas/${id}`, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function cambiarEstadoFactura(
  id: string,
  estado: 'pendiente' | 'abonada',
): Promise<Factura> {
  return api.patch<Factura>(`/api/v1/facturas/${id}/estado`, { estado });
}

export async function eliminarFactura(id: string): Promise<void> {
  return api.del<void>(`/api/v1/facturas/${id}`);
}

export async function descargarArchivo(id: string): Promise<Blob> {
  const response = await apiClient.get(`/api/v1/facturas/${id}/archivo`, {
    responseType: 'blob',
  });
  return response.data;
}
