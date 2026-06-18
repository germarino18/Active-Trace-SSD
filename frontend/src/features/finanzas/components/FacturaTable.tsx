import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Factura, EstadoFactura } from '../types/facturas';
import * as facturasService from '../services/facturas.service';

const estadoConfig: Record<EstadoFactura, { label: string; className: string }> = {
  pendiente: {
    label: 'Pendiente',
    className: 'bg-warning/10 text-warning',
  },
  abonada: {
    label: 'Abonada',
    className: 'bg-success/10 text-success',
  },
};

function formatearTamano(bytes?: number): string {
  if (!bytes) return '-';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatearFecha(iso: string): string {
  return new Date(iso).toLocaleDateString('es-AR');
}

interface FacturaTableProps {
  facturas: Factura[];
  isLoading: boolean;
  onEdit: (factura: Factura) => void;
  onDelete: (factura: Factura) => void;
  onToggleEstado: (factura: Factura) => void;
}

export function FacturaTable({
  facturas,
  isLoading,
  onEdit,
  onDelete,
  onToggleEstado,
}: FacturaTableProps) {
  const handleDescargar = async (factura: Factura, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const blob = await facturasService.descargarArchivo(factura.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = factura.archivo_nombre ?? 'archivo';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      // Silently fail
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!facturas || facturas.length === 0) {
    return <EmptyState message="No se encontraron facturas" icon="receipt_long" />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left text-label-md">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="px-4 py-3 font-medium text-on-surface">Fecha carga</th>
            <th className="px-4 py-3 font-medium text-on-surface">Docente</th>
            <th className="px-4 py-3 font-medium text-on-surface">Período</th>
            <th className="px-4 py-3 font-medium text-on-surface">Detalle</th>
            <th className="px-4 py-3 font-medium text-on-surface">Archivo</th>
            <th className="px-4 py-3 font-medium text-on-surface">Tamaño</th>
            <th className="px-4 py-3 font-medium text-on-surface">Estado</th>
            <th className="px-4 py-3 font-medium text-on-surface">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {facturas.map((factura) => {
            const est = estadoConfig[factura.estado];
            return (
              <tr
                key={factura.id}
                className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
              >
                <td className="px-4 py-3 text-on-surface-variant">
                  {formatearFecha(factura.fecha_carga)}
                </td>
                <td className="px-4 py-3 text-on-surface font-medium">
                  {factura.docente_nombre}
                </td>
                <td className="px-4 py-3 text-on-surface-variant">
                  {factura.periodo}
                </td>
                <td className="px-4 py-3 text-on-surface-variant max-w-[200px] truncate">
                  {factura.detalle}
                </td>
                <td className="px-4 py-3">
                  {factura.archivo_nombre ? (
                    <button
                      type="button"
                      onClick={(e) => handleDescargar(factura, e)}
                      className="inline-flex items-center gap-1 rounded-lg bg-surface-container-low px-2.5 py-1 text-label-xs font-medium text-primary transition-colors hover:bg-primary/10"
                      title="Descargar archivo"
                    >
                      <span className="material-symbols-outlined text-[14px]">download</span>
                      {factura.archivo_nombre}
                    </button>
                  ) : (
                    <span className="text-on-surface-variant">-</span>
                  )}
                </td>
                <td className="px-4 py-3 text-on-surface-variant">
                  {formatearTamano(factura.archivo_tamano)}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${est.className}`}
                  >
                    <span className="sr-only">Estado:</span>
                    {est.label}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => onToggleEstado(factura)}
                      className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                      title={factura.estado === 'pendiente' ? 'Marcar como abonada' : 'Volver a pendiente'}
                    >
                      <span className="material-symbols-outlined text-[18px]">
                        {factura.estado === 'pendiente' ? 'check_circle' : 'undo'}
                      </span>
                    </button>
                    <button
                      type="button"
                      onClick={() => onEdit(factura)}
                      className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                      title="Editar"
                    >
                      <span className="material-symbols-outlined text-[18px]">edit</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => onDelete(factura)}
                      className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-error"
                      title="Eliminar"
                    >
                      <span className="material-symbols-outlined text-[18px]">delete</span>
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
