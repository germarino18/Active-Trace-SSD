import { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  usePadronDictado,
  useMutationAgregarAlumnosBulk,
  useMutationQuitarAlumnosBulk,
  useAlumnosDisponibles,
} from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import type { AlumnoDisponible, EntradaPadron } from '../types';

// ---------- AgregarAlumnosForm ----------

function AgregarAlumnosForm({
  dictadoId,
  disponibles,
  loadingDisponibles,
  onClose,
}: {
  dictadoId: string;
  disponibles: AlumnoDisponible[] | undefined;
  loadingDisponibles: boolean;
  onClose: () => void;
}) {
  const [selected, setSelected] = useState<string[]>([]);
  const agregarBulkMutation = useMutationAgregarAlumnosBulk(dictadoId);

  const toggleSelect = (usuarioId: string) => {
    setSelected((prev) =>
      prev.includes(usuarioId) ? prev.filter((id) => id !== usuarioId) : [...prev, usuarioId],
    );
  };

  const handleSubmit = useCallback(async () => {
    if (selected.length === 0) return;
    await agregarBulkMutation.mutateAsync(selected);
    setSelected([]);
    onClose();
  }, [selected, agregarBulkMutation, onClose]);

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
      <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
        Agregar alumnos al padrón
      </h4>

      {loadingDisponibles ? (
        <p style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>Cargando alumnos disponibles…</p>
      ) : !disponibles || disponibles.length === 0 ? (
        <p style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>
          No hay alumnos disponibles para agregar (todos ya están en el padrón).
        </p>
      ) : (
        <div className="space-y-2">
          <p style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>
            Seleccioná uno o más alumnos para agregar al padrón:
          </p>
          <div
            style={{ maxHeight: 240, overflowY: 'auto', border: '1px solid var(--outline-variant)', borderRadius: 8 }}
          >
            {disponibles.map((alumno: AlumnoDisponible) => (
              <label
                key={alumno.usuario_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '8px 12px',
                  cursor: 'pointer',
                  borderBottom: '1px solid var(--outline-variant)',
                  background: selected.includes(alumno.usuario_id)
                    ? 'color-mix(in srgb, var(--primary) 8%, transparent)'
                    : undefined,
                }}
              >
                <input
                  type="checkbox"
                  checked={selected.includes(alumno.usuario_id)}
                  onChange={() => toggleSelect(alumno.usuario_id)}
                  className="h-4 w-4"
                />
                <span style={{ fontSize: 14, color: 'var(--on-surface)' }}>
                  {alumno.apellidos}, {alumno.nombre}
                  {alumno.email ? (
                    <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginLeft: 8 }}>
                      {alumno.email}
                    </span>
                  ) : null}
                </span>
              </label>
            ))}
          </div>
          {selected.length > 0 && (
            <p style={{ fontSize: 12, color: 'var(--primary)' }}>
              {selected.length} alumno{selected.length !== 1 ? 's' : ''} seleccionado{selected.length !== 1 ? 's' : ''}
            </p>
          )}
        </div>
      )}

      <div style={{ display: 'flex', gap: 8 }}>
        <Button
          type="button"
          variant="primary"
          size="sm"
          disabled={agregarBulkMutation.isPending || loadingDisponibles || selected.length === 0}
          onClick={handleSubmit}
        >
          {agregarBulkMutation.isPending ? 'Guardando…' : `Agregar${selected.length > 0 ? ` (${selected.length})` : ''}`}
        </Button>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          onClick={() => { setSelected([]); onClose(); }}
        >
          Cancelar
        </Button>
      </div>
      {agregarBulkMutation.isError && (
        <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al agregar los alumnos</p>
      )}
    </div>
  );
}

// ---------- Main Page ----------

export function AlumnosDictadoPage() {
  const { dictadoId } = useParams<{ dictadoId: string }>();
  const [showForm, setShowForm] = useState(false);
  const [selectedPadron, setSelectedPadron] = useState<string[]>([]);
  const [confirmBulkBaja, setConfirmBulkBaja] = useState(false);

  const { data, isLoading, isError } = usePadronDictado(dictadoId!);
  const { data: disponibles, isLoading: loadingDisponibles } = useAlumnosDisponibles(dictadoId!);
  const quitarBulkMutation = useMutationQuitarAlumnosBulk(dictadoId!);

  const togglePadronSelect = (id: string) => {
    setSelectedPadron((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const toggleAll = () => {
    if (!data) return;
    const allIds = data.map((a: EntradaPadron) => a.id);
    if (selectedPadron.length === allIds.length) {
      setSelectedPadron([]);
    } else {
      setSelectedPadron(allIds);
    }
  };

  const handleBulkBaja = useCallback(async () => {
    if (selectedPadron.length === 0) return;
    await quitarBulkMutation.mutateAsync(selectedPadron);
    setSelectedPadron([]);
    setConfirmBulkBaja(false);
  }, [selectedPadron, quitarBulkMutation]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>Padrón de Alumnos</h3>
        <Button variant="primary" size="sm" onClick={() => setShowForm((v) => !v)}>
          <span className="material-symbols-outlined text-[16px]">person_add</span>
          Agregar alumno
        </Button>
      </div>

      {showForm && (
        <AgregarAlumnosForm
          dictadoId={dictadoId!}
          disponibles={disponibles}
          loadingDisponibles={loadingDisponibles}
          onClose={() => setShowForm(false)}
        />
      )}

      {selectedPadron.length > 0 && !confirmBulkBaja && (
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-3 flex items-center gap-3 flex-wrap">
          <span style={{ fontSize: 14, color: 'var(--on-surface)' }}>
            {selectedPadron.length} alumno{selectedPadron.length !== 1 ? 's' : ''} seleccionado{selectedPadron.length !== 1 ? 's' : ''}
          </span>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setConfirmBulkBaja(true)}
          >
            <span className="material-symbols-outlined text-[14px]">person_remove</span>
            Dar de baja seleccionados
          </Button>
          <Button variant="secondary" size="sm" onClick={() => setSelectedPadron([])}>
            Limpiar selección
          </Button>
        </div>
      )}

      {confirmBulkBaja && (
        <div className="rounded-xl border border-error/30 bg-error/5 p-4 space-y-3">
          <p style={{ margin: 0, fontSize: 14, color: 'var(--on-surface)' }}>
            ¿Confirmás dar de baja {selectedPadron.length} alumno{selectedPadron.length !== 1 ? 's' : ''} del padrón?
            Sus calificaciones quedarán guardadas.
          </p>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button
              variant="primary"
              size="sm"
              onClick={handleBulkBaja}
              disabled={quitarBulkMutation.isPending}
            >
              {quitarBulkMutation.isPending ? 'Eliminando…' : 'Confirmar baja'}
            </Button>
            <Button variant="secondary" size="sm" onClick={() => setConfirmBulkBaja(false)}>Cancelar</Button>
          </div>
        </div>
      )}

      {isLoading ? (
        <LoadingState rows={5} cols={4} />
      ) : isError ? (
        <EmptyState message="Error al cargar el padrón" icon="error" />
      ) : !data || data.length === 0 ? (
        <EmptyState message="No hay alumnos en el padrón" icon="group" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3">
                  <input
                    type="checkbox"
                    aria-label="Seleccionar todos"
                    checked={selectedPadron.length === data.length && data.length > 0}
                    onChange={toggleAll}
                    className="h-4 w-4"
                  />
                </th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Apellidos</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Email</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Comisión</th>
              </tr>
            </thead>
            <tbody>
              {data.map((alumno: EntradaPadron) => (
                <tr
                  key={alumno.id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                  style={selectedPadron.includes(alumno.id)
                    ? { background: 'color-mix(in srgb, var(--primary) 6%, transparent)' }
                    : undefined}
                >
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      aria-label={`Seleccionar ${alumno.nombre} ${alumno.apellidos}`}
                      checked={selectedPadron.includes(alumno.id)}
                      onChange={() => togglePadronSelect(alumno.id)}
                      className="h-4 w-4"
                    />
                  </td>
                  <td className="px-4 py-3 text-body-sm text-on-surface">{alumno.nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface">{alumno.apellidos}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{alumno.email ?? '—'}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{alumno.comision ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
