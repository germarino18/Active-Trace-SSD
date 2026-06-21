import { useState, useEffect, useRef, useCallback } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button, Input } from '@/shared/components/ds';
import { ConfirmDialog } from '@/features/coordinacion/components/ConfirmDialog';
import { AxiosError } from 'axios';
import {
  useCarreras,
  useCrearCarrera,
  useActualizarCarrera,
  useEliminarCarrera,
  useToggleCarreraEstado,
} from '../hooks/useEstructura';
import type { Carrera, CrearCarreraData, ActualizarCarreraData } from '../types';

export function CarrerasPage() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data, isLoading, isError } = useCarreras(debouncedQuery ? { q: debouncedQuery } : undefined);
  const crear = useCrearCarrera();
  const actualizar = useActualizarCarrera();
  const eliminar = useEliminarCarrera();
  const toggleEstado = useToggleCarreraEstado();

  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Carrera | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Carrera | null>(null);
  const [form, setForm] = useState<CrearCarreraData>({ codigo: '', nombre: '' });
  const [toggleError, setToggleError] = useState<string | null>(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query]);

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

  async function handleSubmit() {
    try {
      if (editTarget) {
        await actualizar.mutateAsync({ id: editTarget.id, data: form as ActualizarCarreraData });
      } else {
        await crear.mutateAsync(form);
      }
      setModalOpen(false);
    } catch {
      // Error handled by mutation — modal stays open for retry
    }
  }

  const handleToggle = useCallback((id: string) => {
    setToggleError(null);
    toggleEstado.mutate(id, {
      onError: (err) => {
        if (err instanceof AxiosError && err.response?.status === 422) {
          const detail = err.response.data?.detail;
          setToggleError(typeof detail === 'string' ? detail : 'No se puede desactivar: la carrera tiene cohortes abiertas');
        } else {
          setToggleError(err.message || 'Error al cambiar estado');
        }
      },
    });
  }, [toggleEstado]);

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

      <div className="relative">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-outline">search</span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar carreras..."
          className="w-full rounded-lg border border-outline-variant bg-surface pl-9 pr-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
        />
      </div>

      {toggleError && (
        <div className="rounded-lg border border-warning/30 bg-warning/5 px-3 py-2 text-label-sm text-warning flex items-center gap-1">
          <span className="material-symbols-outlined text-[16px]">warning</span>
          {toggleError}
          <button type="button" onClick={() => setToggleError(null)} className="ml-auto text-outline hover:text-on-surface">
            <span className="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>
      )}

      {isLoading ? (
        <LoadingState rows={4} cols={4} />
      ) : isError ? (
        <EmptyState message="Error al cargar carreras" icon="error" />
      ) : carreras.length === 0 ? (
        <EmptyState message={query ? 'No se encontraron carreras' : 'No hay carreras registradas'} icon="school" />
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
                {editTarget ? 'Editar carrera' : 'Nueva carrera'}
              </h1>
              <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>
                {editTarget ? 'Modificá los datos de la carrera.' : 'Ingresá los datos de la nueva carrera.'}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <Input
                  label="Código"
                  icon="tag"
                  placeholder="Ej: ING-SIS"
                  value={form.codigo}
                  onChange={(e) => setForm((f) => ({ ...f, codigo: e.target.value }))}
                />
                <Input
                  label="Nombre"
                  icon="school"
                  placeholder="Ej: Ingeniería en Sistemas"
                  value={form.nombre}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 28 }}>
                <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancelar</Button>
                <Button type="button" variant="primary" onClick={handleSubmit} disabled={isPending || !form.codigo || !form.nombre}>
                  {editTarget ? 'Guardar cambios' : 'Crear carrera'}
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
        title="Eliminar carrera"
        message={`¿Estás seguro de que querés eliminar la carrera "${deleteTarget?.nombre}"?`}
        confirmLabel="Eliminar"
        variant="danger"
        cascadeWarning="Esta acción eliminará la carrera de forma permanente."
      />
    </div>
  );
}
