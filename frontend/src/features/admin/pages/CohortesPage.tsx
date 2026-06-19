import { useState, useEffect, useRef, useCallback } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button, Input } from '@/shared/components/ds';
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
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data, isLoading, isError } = useCohortes(debouncedQuery ? { q: debouncedQuery } : undefined);
  const crear = useCrearCohorte();
  const actualizar = useActualizarCohorte();
  const eliminar = useEliminarCohorte();
  const toggleEstado = useToggleCohorteEstado();

  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Cohorte | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Cohorte | null>(null);
  const [form, setForm] = useState<CrearCohorteData>(emptyForm);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query]);

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

  async function handleSubmit() {
    const payload = {
      ...form,
      vigencia_hasta: form.vigencia_hasta || undefined,
    };
    try {
      if (editTarget) {
        await actualizar.mutateAsync({ id: editTarget.id, data: payload as ActualizarCohorteData });
      } else {
        await crear.mutateAsync(payload);
      }
      setModalOpen(false);
    } catch {
      // Error handled by mutation — modal stays open for retry
    }
  }

  const handleToggle = useCallback((id: string) => {
    toggleEstado.mutate(id);
  }, [toggleEstado]);

  const isPending = crear.isPending || actualizar.isPending;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-body-sm text-on-surface-variant">
          {data?.total ?? 0} cohorte(s) registrado(s)
        </p>
        <Button type="button" variant="primary" icon="add" onClick={openCreate}>Nuevo cohorte</Button>
      </div>

      <div className="relative">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-outline">search</span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar cohortes..."
          className="w-full rounded-lg border border-outline-variant bg-surface pl-9 pr-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
        />
      </div>

      {isLoading ? (
        <LoadingState rows={4} cols={6} />
      ) : isError ? (
        <EmptyState message="Error al cargar cohortes" icon="error" />
      ) : cohortes.length === 0 ? (
        <EmptyState message={query ? 'No se encontraron cohortes' : 'No hay cohortes registrados'} icon="group" />
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
                        c.estado === 'Activo' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'
                      }`}
                    >
                      {c.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => handleToggle(c.id)}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                        title={c.estado === 'Activo' ? 'Desactivar' : 'Activar'}
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          {c.estado === 'Activo' ? 'toggle_off' : 'toggle_on'}
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
          <div style={{ width: 400, maxWidth: '100%' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ background: 'var(--surface-container)', border: '1px solid var(--outline-variant)', borderRadius: 'var(--radius-lg)', padding: 28 }}>
              <h1 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
                {editTarget ? 'Editar cohorte' : 'Nuevo cohorte'}
              </h1>
              <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>
                {editTarget ? 'Modificá los datos del cohorte.' : 'Ingresá los datos del nuevo cohorte.'}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <Input
                  label="Nombre"
                  icon="calendar_view_month"
                  placeholder="Ej: Cohorte 2024"
                  value={form.nombre}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                />
                <Input
                  label="Año inicio"
                  icon="calendar_month"
                  type="number"
                  value={String(form.anio_inicio)}
                  onChange={(e) => setForm((f) => ({ ...f, anio_inicio: Number(e.target.value) }))}
                />
                <Input
                  label="Vigencia desde"
                  icon="date_range"
                  type="date"
                  value={form.vigencia_desde}
                  onChange={(e) => setForm((f) => ({ ...f, vigencia_desde: e.target.value }))}
                />
                <Input
                  label="Vigencia hasta"
                  icon="event"
                  type="date"
                  value={form.vigencia_hasta ?? ''}
                  onChange={(e) => setForm((f) => ({ ...f, vigencia_hasta: e.target.value }))}
                  helper="Opcional"
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 28 }}>
                <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancelar</Button>
                <Button type="button" variant="primary" onClick={handleSubmit} disabled={isPending || !form.nombre || !form.vigencia_desde}>
                  {editTarget ? 'Guardar cambios' : 'Crear cohorte'}
                </Button>
              </div>
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
