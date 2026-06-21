import { useState, useEffect, useRef, useCallback } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import { ConfirmDialog } from '@/features/coordinacion/components/ConfirmDialog';
import {
  useDictados,
  useCrearDictado,
  useActualizarDictado,
  useEliminarDictado,
  useToggleDictadoEstado,
} from '../hooks/useDictados';
import { useCarreras, useCohortes, useMaterias } from '../hooks/useEstructura';
import { DictadoFormModal } from '../components/DictadoFormModal';
import type { Dictado, CrearDictadoData, ActualizarDictadoData } from '../types/dictados';

export function DictadosPage() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data, isLoading, isError } = useDictados(debouncedQuery ? { q: debouncedQuery } : undefined);
  const { data: carrerasData } = useCarreras({ activa: true });
  const { data: cohortesData } = useCohortes({ activa: true });
  const { data: materiasData } = useMaterias({ activa: true });
  const crear = useCrearDictado();
  const actualizar = useActualizarDictado();
  const eliminar = useEliminarDictado();
  const toggleEstado = useToggleDictadoEstado();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query]);

  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Dictado | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Dictado | null>(null);

  const dictados = data?.items ?? [];
  const carreras = carrerasData?.items ?? [];
  const cohortes = cohortesData?.items ?? [];
  const materias = materiasData?.items ?? [];

  const materiaMap = Object.fromEntries(materias.map((m) => [m.id, m.nombre]));
  const carreraMap = Object.fromEntries(carreras.map((c) => [c.id, c.nombre]));
  const cohorteMap = Object.fromEntries(cohortes.map((c) => [c.id, c.nombre]));

  function openCreate() {
    setEditTarget(null);
    setModalOpen(true);
  }

  function openEdit(d: Dictado) {
    setEditTarget(d);
    setModalOpen(true);
  }

  const handleSave = useCallback(async (formData: CrearDictadoData | ActualizarDictadoData) => {
    if (editTarget) {
      await actualizar.mutateAsync({ id: editTarget.id, data: formData as ActualizarDictadoData });
    } else {
      await crear.mutateAsync(formData as CrearDictadoData);
    }
  }, [editTarget, actualizar, crear]);

  const handleToggle = useCallback((id: string) => {
    toggleEstado.mutate(id);
  }, [toggleEstado]);

  const isPending = crear.isPending || actualizar.isPending;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-body-sm text-on-surface-variant">
          {data?.total ?? 0} dictado(s) registrado(s)
        </p>
        <Button type="button" variant="primary" icon="add" onClick={openCreate}>
          Nuevo dictado
        </Button>
      </div>

      <div className="relative">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-outline">search</span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar dictados..."
          className="w-full rounded-lg border border-outline-variant bg-surface pl-9 pr-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
        />
      </div>

      {isLoading ? (
        <LoadingState rows={4} cols={6} />
      ) : isError ? (
        <EmptyState message="Error al cargar dictados" icon="error" />
      ) : dictados.length === 0 ? (
        <EmptyState message={query ? 'No se encontraron dictados' : 'No hay dictados registrados'} icon="menu_book" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Materia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Carrera</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Cohorte</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Vigencia</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {dictados.map((d: Dictado) => (
                <tr key={d.id} className="border-b border-outline-variant transition-colors hover:bg-surface-container-low">
                  <td className="px-4 py-3 text-body-sm font-medium text-on-surface">{materiaMap[d.materia_id] ?? d.materia_id}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{carreraMap[d.carrera_id] ?? '—'}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{cohorteMap[d.cohorte_id] ?? '—'}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {d.vig_desde ? `${new Date(d.vig_desde).toLocaleDateString('es-AR')}` : '—'}
                    {d.vig_hasta ? ` → ${new Date(d.vig_hasta).toLocaleDateString('es-AR')}` : ''}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${
                        d.estado === 'Activo' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'
                      }`}
                    >
                      {d.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => handleToggle(d.id)}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                        title={d.estado === 'Activo' ? 'Desactivar' : 'Activar'}
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          {d.estado === 'Activo' ? 'toggle_off' : 'toggle_on'}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => openEdit(d)}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                        title="Editar"
                      >
                        <span className="material-symbols-outlined text-[18px]">edit</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setDeleteTarget(d)}
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

      <DictadoFormModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditTarget(null); }}
        onSave={handleSave}
        selectedItem={editTarget}
        carreras={carreras}
        cohortes={cohortes}
        materias={materias}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) eliminar.mutate(deleteTarget.id);
        }}
        title="Eliminar dictado"
        message={`¿Estás seguro de que querés eliminar el dictado de "${deleteTarget ? (materiaMap[deleteTarget.materia_id] ?? deleteTarget.materia_id) : ''}"?`}
        confirmLabel="Eliminar"
        variant="danger"
        cascadeWarning="Esta acción eliminará el dictado de forma permanente."
      />
    </div>
  );
}
