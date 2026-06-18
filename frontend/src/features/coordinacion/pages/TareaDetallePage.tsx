import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTarea, useCambiarEstado, useAgregarComentario, useDelegarTarea } from '../hooks/useTareas';
import { TareaStateBadge } from '../components/TareaStateBadge';
import { CommentThread } from '../components/CommentThread';
import { Spinner } from '@/shared/components/Spinner';

type TareaEstado = 'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada';

const TRANSITIONS: Record<TareaEstado, { to: TareaEstado; label: string; requiresReason: boolean }[]> = {
  Pendiente: [
    { to: 'En progreso', label: 'Iniciar', requiresReason: false },
    { to: 'Cancelada', label: 'Cancelar', requiresReason: true },
  ],
  'En progreso': [
    { to: 'Resuelta', label: 'Resolver', requiresReason: false },
    { to: 'Cancelada', label: 'Cancelar', requiresReason: true },
  ],
  Resuelta: [],
  Cancelada: [],
};

export function TareaDetallePage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: tarea, isLoading } = useTarea(id);
  const cambiarEstado = useCambiarEstado();
  const agregarComentario = useAgregarComentario();
  const delegarTarea = useDelegarTarea();

  const [razonCancelacion, setRazonCancelacion] = useState('');
  const [showCancelInput, setShowCancelInput] = useState(false);
  const [cancelTargetEstado, setCancelTargetEstado] = useState<TareaEstado | null>(null);

  const [nuevoAsignadoId, setNuevoAsignadoId] = useState('');
  const [showDelegar, setShowDelegar] = useState(false);

  const handleCambiarEstado = async (nuevoEstado: TareaEstado, requiereReason: boolean) => {
    if (!id) return;
    if (requiereReason) {
      setCancelTargetEstado(nuevoEstado);
      setShowCancelInput(true);
      return;
    }
    try {
      await cambiarEstado.mutateAsync({ tareaId: id, estado: nuevoEstado });
    } catch {
      // handled by mutation error state
    }
  };

  const handleCancelConfirm = async () => {
    if (!id || !cancelTargetEstado || !razonCancelacion.trim()) return;
    try {
      await cambiarEstado.mutateAsync({
        tareaId: id,
        estado: cancelTargetEstado,
        razon: razonCancelacion.trim(),
      });
      setShowCancelInput(false);
      setRazonCancelacion('');
      setCancelTargetEstado(null);
    } catch {
      // handled by mutation error state
    }
  };

  const handleDelegar = async () => {
    if (!id || !nuevoAsignadoId.trim()) return;
    try {
      await delegarTarea.mutateAsync({ tareaId: id, nuevoAsignadoId: nuevoAsignadoId.trim() });
      setShowDelegar(false);
      setNuevoAsignadoId('');
    } catch {
      // handled by mutation error state
    }
  };

  const handleAddComment = async (contenido: string) => {
    if (!id) return;
    await agregarComentario.mutateAsync({ tareaId: id, contenido });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!tarea) {
    return (
      <div className="rounded-xl border border-error/30 bg-error/5 p-4 text-body-sm text-error">
        Tarea no encontrada.
      </div>
    );
  }

  const availableTransitions = TRANSITIONS[tarea.estado] ?? [];

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="mb-2 inline-flex items-center gap-1 text-label-sm text-primary hover:underline"
        >
          <span className="material-symbols-outlined text-[16px]">arrow_back</span>
          Volver
        </button>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="font-headline-lg text-headline-lg text-on-surface">{tarea.titulo}</h2>
            <TareaStateBadge estado={tarea.estado} />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="text-label-xs text-outline uppercase tracking-wider">Asignado a</span>
            <p className="text-body-sm text-on-surface">{tarea.asignado_nombre}</p>
          </div>
          <div>
            <span className="text-label-xs text-outline uppercase tracking-wider">Asignado por</span>
            <p className="text-body-sm text-on-surface">{tarea.asignado_por_nombre}</p>
          </div>
          {tarea.materia_nombre && (
            <div>
              <span className="text-label-xs text-outline uppercase tracking-wider">Materia</span>
              <p className="text-body-sm text-on-surface">{tarea.materia_nombre}</p>
            </div>
          )}
          <div>
            <span className="text-label-xs text-outline uppercase tracking-wider">Creada</span>
            <p className="text-body-sm text-on-surface">
              {new Date(tarea.created_at).toLocaleString('es-AR')}
            </p>
          </div>
        </div>

        {tarea.descripcion && (
          <div>
            <span className="text-label-xs text-outline uppercase tracking-wider">Descripción</span>
            <p className="mt-1 text-body-sm text-on-surface-variant whitespace-pre-wrap">{tarea.descripcion}</p>
          </div>
        )}

        {tarea.razon_cancelacion && (
          <div className="rounded-lg border border-error/20 bg-error/5 p-3">
            <span className="text-label-xs text-outline uppercase tracking-wider">Motivo de cancelación</span>
            <p className="mt-1 text-body-sm text-error">{tarea.razon_cancelacion}</p>
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {availableTransitions.map((transition) => (
          <button
            key={transition.to}
            type="button"
            onClick={() => handleCambiarEstado(transition.to, transition.requiresReason)}
            disabled={cambiarEstado.isPending}
            className="inline-flex items-center gap-1 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {transition.label}
          </button>
        ))}
        {tarea.estado !== 'Cancelada' && tarea.estado !== 'Resuelta' && (
          <button
            type="button"
            onClick={() => setShowDelegar(!showDelegar)}
            className="inline-flex items-center gap-1 rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            <span className="material-symbols-outlined text-[16px]">swap_horiz</span>
            Delegar
          </button>
        )}
      </div>

      {showCancelInput && (
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
          <label className="block text-label-sm text-on-surface-variant">
            Motivo de cancelación
          </label>
          <textarea
            value={razonCancelacion}
            onChange={(e) => setRazonCancelacion(e.target.value)}
            rows={3}
            placeholder="Explicá el motivo..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleCancelConfirm}
              disabled={!razonCancelacion.trim() || cambiarEstado.isPending}
              className="inline-flex items-center gap-1 rounded-lg bg-error px-4 py-2 text-label-sm font-medium text-on-error transition-colors hover:bg-error/90 disabled:opacity-50"
            >
              Confirmar cancelación
            </button>
            <button
              type="button"
              onClick={() => { setShowCancelInput(false); setRazonCancelacion(''); setCancelTargetEstado(null); }}
              className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
            >
              Volver
            </button>
          </div>
        </div>
      )}

      {showDelegar && (
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
          <label className="block text-label-sm text-on-surface-variant">
            Nuevo asignado (ID)
          </label>
          <input
            type="text"
            value={nuevoAsignadoId}
            onChange={(e) => setNuevoAsignadoId(e.target.value)}
            placeholder="ID del usuario"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleDelegar}
              disabled={!nuevoAsignadoId.trim() || delegarTarea.isPending}
              className="inline-flex items-center gap-1 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              Delegar
            </button>
            <button
              type="button"
              onClick={() => { setShowDelegar(false); setNuevoAsignadoId(''); }}
              className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
        <CommentThread
          comentarios={tarea.comentarios}
          onAddComment={handleAddComment}
        />
      </div>
    </div>
  );
}
