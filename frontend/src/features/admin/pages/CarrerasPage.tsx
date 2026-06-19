import { useState } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import { ConfirmDialog } from '@/features/coordinacion/components/ConfirmDialog';
import {
  useCarreras,
  useCrearCarrera,
  useActualizarCarrera,
  useEliminarCarrera,
  useToggleCarreraEstado,
} from '../hooks/useEstructura';
import type { Carrera, CrearCarreraData, ActualizarCarreraData } from '../types';

export function CarrerasPage() {
  const { data, isLoading, isError } = useCarreras();
  const crear = useCrearCarrera();
  const actualizar = useActualizarCarrera();
  const eliminar = useEliminarCarrera();
  const toggleEstado = useToggleCarreraEstado();

  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Carrera | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Carrera | null>(null);
  const [form, setForm] = useState<CrearCarreraData>({ codigo: '', nombre: '' });

  const carreras = data?.items ?? [];

  function openCreate() {
    setEditTarget(null);
    setForm({ codigo: '', nombre: '' });
    setModalOpen(true);
  }

  function openEdit(c: Carrera) {
    setEditTarget(c);
    setForm({ codigo: c.codigo, nombre: c.nombre });
    setModalOpen(true);
  }

  function handleSubmit() {
    if (editTarget) {
      actualizar.mutate(
        { id: editTarget.id, data: form as ActualizarCarreraData },
        { onSuccess: () => setModalOpen(false) },
      );
    } else {
      crear.mutate(form, { onSuccess: () => setModalOpen(false) });
    }
  }

  const isPending = crear.isPending || actualizar.isPending;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-body-sm text-on-surface-variant">
          {data?.total ?? 0} carrera(s) registrada(s)
        </p>
        <Button type="button" variant="primary" icon="add" onClick={openCreate}>
          Nueva carrera
        </Button>
      </div>

      {isLoading ? (
        <LoadingState rows={4} cols={4} />
      ) : isError ? (
        <EmptyState message="Error al cargar carreras" icon="error" />
      ) : carreras.length === 0 ? (
        <EmptyState message="No hay carreras registradas" icon="school" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Código</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {carreras.map((c: Carrera) => (
                <tr key={c.id} className="border-b border-outline-variant transition-colors hover:bg-surface-container-low">
                  <td className="px-4 py-3 text-body-sm font-medium text-on-surface">{c.codigo}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{c.nombre}</td>
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
              {editTarget ? 'Editar carrera' : 'Nueva carrera'}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-label-sm text-on-surface-variant">Código</label>
                <input
                  type="text"
                  value={form.codigo}
                  onChange={(e) => setForm((f) => ({ ...f, codigo: e.target.value }))}
                  className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
                  placeholder="Ej: MAT-101"
                />
              </div>
              <div>
                <label className="mb-1 block text-label-sm text-on-surface-variant">Nombre</label>
                <input
                  type="text"
                  value={form.nombre}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                  className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
                  placeholder="Ej: Matemática I"
                />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button type="button" variant="primary" onClick={handleSubmit} disabled={isPending || !form.codigo || !form.nombre}>
                {editTarget ? 'Guardar cambios' : 'Crear carrera'}
              </Button>
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
        title="Eliminar carrera"
        message={`¿Estás seguro de que querés eliminar la carrera "${deleteTarget?.nombre}"?`}
        confirmLabel="Eliminar"
        variant="danger"
        cascadeWarning="Esta acción eliminará la carrera de forma permanente."
      />
    </div>
  );
}
