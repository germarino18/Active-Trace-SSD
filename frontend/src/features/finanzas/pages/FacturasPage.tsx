import { useState, useCallback } from 'react';
import { useFacturas, useCrearFactura, useEditarFactura, useEliminarFactura, useCambiarEstadoFactura } from '../hooks/useFacturas';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { FacturaFilters, type FacturaFilterValues } from '../components/FacturaFilters';
import { FacturaTable } from '../components/FacturaTable';
import { FacturaFormModal } from '../components/FacturaFormModal';
import { FacturaDeleteConfirmModal } from '../components/FacturaDeleteConfirmModal';
import { HelpButton } from '@/features/coordinacion/components/HelpButton';
import type { Factura } from '../types/facturas';

const initialFilters: FacturaFilterValues = {
  docente: '',
  estado: '',
  fecha_desde: '',
  fecha_hasta: '',
  q: '',
};

export function FacturasPage() {
  const { hasPermission } = useAuth();
  const [filters, setFilters] = useState<FacturaFilterValues>(initialFilters);
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const [showFormModal, setShowFormModal] = useState(false);
  const [editingFactura, setEditingFactura] = useState<Factura | null>(null);
  const [deletingFactura, setDeletingFactura] = useState<Factura | null>(null);

  const canCreate = hasPermission('finanzas:facturas:crear');
  const canEdit = hasPermission('finanzas:facturas:editar');
  const canDelete = hasPermission('finanzas:facturas:eliminar');
  const canChangeEstado = hasPermission('finanzas:facturas:cambiar-estado');

  const appliedFilters = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== '' && v !== undefined),
  );

  const { data, isLoading, isError } = useFacturas({
    ...appliedFilters,
    offset: page * pageSize,
    limit: pageSize,
  });

  const crearFactura = useCrearFactura();
  const editarFactura = useEditarFactura();
  const eliminarFactura = useEliminarFactura();
  const cambiarEstadoFactura = useCambiarEstadoFactura();

  const handleFilterChange = (key: string, value: unknown) => {
    setPage(0);
    setFilters((prev) => ({ ...prev, [key]: value as string }));
  };

  const handleClearFilters = () => {
    setPage(0);
    setFilters(initialFilters);
  };

  const handleOpenCreate = () => {
    setEditingFactura(null);
    setShowFormModal(true);
  };

  const handleOpenEdit = (factura: Factura) => {
    setEditingFactura(factura);
    setShowFormModal(true);
  };

  const handleCloseFormModal = () => {
    setShowFormModal(false);
    setEditingFactura(null);
  };

  const handleSave = useCallback(
    async (formData: FormData) => {
      if (editingFactura) {
        await editarFactura.mutateAsync({ id: editingFactura.id, data: formData });
      } else {
        await crearFactura.mutateAsync(formData);
      }
    },
    [editingFactura, editarFactura, crearFactura],
  );

  const handleDelete = useCallback(async () => {
    if (deletingFactura) {
      await eliminarFactura.mutateAsync(deletingFactura.id);
    }
  }, [deletingFactura, eliminarFactura]);

  const handleToggleEstado = useCallback(
    (factura: Factura) => {
      const nuevoEstado = factura.estado === 'pendiente' ? 'abonada' : 'pendiente';
      cambiarEstadoFactura.mutate({ id: factura.id, estado: nuevoEstado });
    },
    [cambiarEstadoFactura],
  );

  const facturas = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Facturas</h2>
            <p className="text-body-md text-on-surface-variant mt-1">
              Gestioná las facturas de honorarios docentes
            </p>
          </div>
          <HelpButton tooltip="Administrá las facturas de honorarios. Usá los filtros para buscar por docente, estado, rango de fechas o texto libre. Podés crear, editar, cambiar estado y eliminar facturas." />
        </div>
        {canCreate && (
          <button
            type="button"
            onClick={handleOpenCreate}
            className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
          >
            <span className="material-symbols-outlined text-[18px]">add</span>
            Nueva factura
          </button>
        )}
      </div>

      <FacturaFilters
        values={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      {isError ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <span className="material-symbols-outlined text-[48px] text-error mb-3">error</span>
          <p className="text-body-md text-on-surface-variant">Error al cargar las facturas</p>
        </div>
      ) : (
        <>
          <FacturaTable
            facturas={facturas}
            isLoading={isLoading}
            onEdit={canEdit ? handleOpenEdit : () => {}}
            onDelete={canDelete ? setDeletingFactura : () => {}}
            onToggleEstado={canChangeEstado ? handleToggleEstado : () => {}}
          />

          {total > pageSize && (
            <div className="flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container disabled:opacity-50"
              >
                Anterior
              </button>
              <span className="text-label-sm text-on-surface-variant">
                <span className="hidden sm:inline">Página </span>
                {page + 1}
                <span className="hidden sm:inline"> de {totalPages}</span>
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * pageSize >= total}
                className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-sm text-on-surface transition-colors hover:bg-surface-container disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}

      <FacturaFormModal
        isOpen={showFormModal}
        onClose={handleCloseFormModal}
        onSave={handleSave}
        selectedItem={editingFactura}
      />

      <FacturaDeleteConfirmModal
        isOpen={!!deletingFactura}
        onClose={() => setDeletingFactura(null)}
        onConfirm={handleDelete}
        factura={deletingFactura}
      />
    </div>
  );
}
