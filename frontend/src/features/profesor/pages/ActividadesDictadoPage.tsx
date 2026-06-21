/**
 * ActividadesDictadoPage — per-dictado actividades view with calificaciones.
 *
 * D3 (design.md): create + edit actividad forms now live inside an overlay
 * modal (portal to document.body) so they float above overflow-hidden cards.
 * Dual invalidation (actividades + atrasados) on create/edit/delete is
 * handled inside the mutation hooks via invalidateDictadoDerived.
 */
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  useActividadesDictado,
  useCalificacionesDictado,
  usePadronDictado,
  useMutationEditarCalificacion,
  useMutationEliminarActividad,
} from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import { ActividadOverlayModal } from '../components/ActividadOverlayModal';
import { CrearActividadForm } from '../components/CrearActividadForm';
import { EditarActividadForm } from '../components/EditarActividadForm';
import {
  ActividadCard,
  buildVirtualActividades,
  matchGrade,
} from '../components/ActividadCard';
import type { Actividad } from '../types';
import type { EditState } from '../components/ActividadCard';

type ModalMode = { type: 'crear' } | { type: 'editar'; actividad: Actividad };

export function ActividadesDictadoPage() {
  const { dictadoId } = useParams<{ dictadoId: string }>();
  const [modalMode, setModalMode] = useState<ModalMode | null>(null);
  const [editState, setEditState] = useState<EditState | null>(null);
  const [registrarNotaActividadId, setRegistrarNotaActividadId] = useState<string | null>(null);

  const { data: actividades, isLoading: loadingActs } = useActividadesDictado(dictadoId!);
  const { data: calificaciones, isLoading: loadingCals } = useCalificacionesDictado(dictadoId!);
  const { data: padron } = usePadronDictado(dictadoId!);
  const editarMutation = useMutationEditarCalificacion();
  const eliminarMutation = useMutationEliminarActividad(dictadoId!);

  const isLoading = loadingActs || loadingCals;
  const virtualActividades = buildVirtualActividades(actividades ?? [], calificaciones ?? []);

  const handleSaveCalificacion = async () => {
    if (!editState) return;
    const nota = editState.nota !== '' ? parseFloat(editState.nota) : null;
    await editarMutation.mutateAsync({
      calificacionId: editState.calificacionId,
      data: { nota_numerica: nota, aprobado: editState.aprobado ?? undefined },
    });
    setEditState(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>Actividades</h3>
        <Button variant="primary" size="sm" onClick={() => setModalMode({ type: 'crear' })}>
          <span className="material-symbols-outlined text-[16px]">add</span>
          Crear actividad
        </Button>
      </div>

      {/* Portal overlay modal — floats above overflow-hidden cards (D3) */}
      <ActividadOverlayModal open={modalMode !== null} onClose={() => setModalMode(null)}>
        {modalMode?.type === 'crear' && (
          <CrearActividadForm dictadoId={dictadoId!} onClose={() => setModalMode(null)} />
        )}
        {modalMode?.type === 'editar' && (
          <EditarActividadForm
            actividad={modalMode.actividad}
            dictadoId={dictadoId!}
            onClose={() => setModalMode(null)}
          />
        )}
      </ActividadOverlayModal>

      {isLoading ? (
        <LoadingState rows={5} cols={4} />
      ) : virtualActividades.length === 0 ? (
        <EmptyState message="No hay actividades ni calificaciones en este dictado" icon="assignment" />
      ) : (
        <div className="space-y-8">
          {virtualActividades.map((act) => (
            <ActividadCard
              key={act.id ?? `legacy-${act.nombre}`}
              act={act}
              dictadoId={dictadoId!}
              cals={(calificaciones ?? []).filter((c) => matchGrade(c, act))}
              padron={padron ?? []}
              editState={editState}
              onStartEdit={setEditState}
              onSave={handleSaveCalificacion}
              onCancelEdit={() => setEditState(null)}
              onChangeEdit={(partial) => setEditState((s) => s ? { ...s, ...partial } : s)}
              isSaving={editarMutation.isPending}
              isRegistrando={registrarNotaActividadId === act.id}
              onRegistrarNota={(actividadId) => setRegistrarNotaActividadId(actividadId)}
              onCloseRegistrar={() => setRegistrarNotaActividadId(null)}
              onEditActividad={act.id !== null ? (a) => setModalMode({ type: 'editar', actividad: a }) : undefined}
              onEliminarActividad={act.id !== null ? (id) => eliminarMutation.mutateAsync(id) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
}
