import { useState } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { ConfirmDialog } from '@/features/coordinacion/components/ConfirmDialog';
import {
  useCohortes,
  useCrearCohorte,
  useActualizarCohorte,
  useEliminarCohorte,
  useToggleCohorteEstado,
} from '../hooks/useEstructura';
import type { Cohorte, CrearCohorteData, ActualizarCohorteData } from '../types';

const emptyForm: CrearCohorteData = {
  nombre: '',
  anio_inicio: new Date().getFullYear(),
  vigencia_desde: '',
  vigencia_hasta: '',
};

export function CohortesPage() {
  const { data, isLoading, isError } = useCohortes();
  const crear = useCrearCohorte();
  const actualizar = useActualizarCohorte();
  const eliminar = useEliminarCohorte();
  const toggleEstado = useToggleCohorteEstado();

  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Cohorte | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Cohorte | null>(null);
  const [form, setForm] = useState<CrearCohorteData>(emptyForm);

  const cohortes = data?.items ?? [];

  function openCreate() {
    setEditTarget(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  function openEdit(c: Cohorte) {
    setEditTarget(c);
    setForm({
      nombre: c.nombre,
      anio_inicio: c.anio_inicio,
      vigencia_desde: c.vigencia_desde,
      vigencia_hasta: c.vigencia_hasta ?? '',
    });
    setModalOpen(true);
  }

  function handleSubmit() {
    const payload = {
      ...form,
      vigencia_hasta: form.vigencia_hasta || undefined,
    };
    if (editTarget) {
      actualizar.mutate(
        { id: editTarget.id, data: payload as ActualizarCohorteData },
        { onSuccess: () => setModalOpen(false) },
      );
    } else {
      crear.mutate(payload, { onSuccess: () => setModalOpen(false) });
    }
  }

  const isPending = crear.isPending || actualizar.isPending;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-body-sm text-on-surface-variant">
          {data?.total ?? 0} cohorte(s) registrado(s)
        </p>
        <button
          type="button"
          onClick={openCreate}
          className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          Nuevo cohorte
        </button>
      </div>

      {isLoading ? (
        <LoadingState rows={4} cols={6} />
      ) : isError ? (
        <EmptyState message="Error al cargar cohortes" icon="error" />
      ) : cohortes.length === 0 ? (
        <EmptyState message="No hay cohortes registrados" icon="group" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Año inicio</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Vigencia desde</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Vigencia hasta</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {cohortes.map((c: Cohorte) => (
                <tr key={c.id} className="border-b border-outline-variant transition-colors hover:bg-surface-container-low">
                  <td className="px-4 py-3 text-body-sm font-medium text-on-surface">{c.nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{c.anio_inicio}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {new Date(c.vigencia_desde).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {c.vigencia_hasta ? new Date(c.vigencia_hasta).toLocaleDateString('es-AR') : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${
                        c.activa ? 'bg-success/10 text-success' : 'bg-error/10 text-error'
                      }`}
                    >
                      {c.activa ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => toggleEstado.mutate(c.id)}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                        title={c.activa ? 'Desactivar' : 'Activar'}
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          {c.activa ? 'toggle_off' : 'toggle_on'}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => openEdit(c)}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                        title="Editar"
                      >
                        <span className="material-symbols-outlined text-[18px]">edit</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setDeleteTarget(c)}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-error"
                        title="Eliminar"
                      >
                        <span className="material-symbols-outlined text-[18px]">delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setModalOpen(false)}>
          <div className="mx-4 w-full max-w-md rounded-xl border border-outline-variant bg-surface p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
            <h3 className="font-headline-lg text-headline-lg text-on-surface mb-4">
              {editTarget ? 'Editar cohorte' : 'Nuevo cohorte'}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-label-sm text-on-surface-variant">Nombre</label>
                <input
                  type="text"
                  value={form.nombre}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                  className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
                  placeholder="Ej: Cohorte 2024"
                />
              </div>
              <div>
                <label className="mb-1 block text-label-sm text-on-surface-variant">Año inicio</label>
                <input
                  type="number"
                  value={form.anio_inicio}
                  onChange={(e) => setForm((f) => ({ ...f, anio_inicio: Number(e.target.value) }))}
                  className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-label-sm text-on-surface-variant">Vigencia desde</label>
                <input
                  type="date"
                  value={form.vigencia_desde}
                  onChange={(e) => setForm((f) => ({ ...f, vigencia_desde: e.target.value }))}
                  className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-label-sm text-on-surface-variant">Vigencia hasta (opcional)</label>
                <input
                  type="date"
                  value={form.vigencia_hasta}
                  onChange={(e) => setForm((f) => ({ ...f, vigencia_hasta: e.target.value }))}
                  className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isPending || !form.nombre || !form.vigencia_desde}
                className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
              >
                {editTarget ? 'Guardar cambios' : 'Crear cohorte'}
              </button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) eliminar.mutate(deleteTarget.id);
        }}
        title="Eliminar cohorte"
        message={`¿Estás seguro de que querés eliminar el cohorte "${deleteTarget?.nombre}"?`}
        confirmLabel="Eliminar"
        variant="danger"
        cascadeWarning="Esta acción eliminará el cohorte de forma permanente."
      />
    </div>
  );
}
