import { useState } from 'react';
import { useLotesPendientes, useAprobarLote, useCancelarLote } from '../hooks/useAprobacionComunicaciones';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { PreviewComunicacionModal } from '@/features/academico/components/PreviewComunicacionModal';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { LoteComunicacion } from '../types';
import type { ComunicacionDestinatario } from '@/features/academico/types';

interface ActionState {
  type: 'success' | 'error';
  message: string;
}

function toLotePreviewDestinatarios(lote: LoteComunicacion): ComunicacionDestinatario[] {
  return (lote.destinatarios ?? []).map((d) => ({
    alumno: { id: d.alumno_id, legajo: '', nombre: d.nombre, apellido: d.apellido, email: d.email, comision: '' },
    asunto: lote.asunto,
    cuerpo: lote.cuerpo,
  }));
}

export function AprobacionComunicacionesPage() {
  const { data, isLoading, isError } = useLotesPendientes();
  const aprobarLote = useAprobarLote();
  const cancelarLote = useCancelarLote();

  const [previewLote, setPreviewLote] = useState<LoteComunicacion | null>(null);
  const [aprobarConfirmLote, setAprobarConfirmLote] = useState<LoteComunicacion | null>(null);
  const [cancelarConfirmLote, setCancelarConfirmLote] = useState<LoteComunicacion | null>(null);
  const [actionState, setActionState] = useState<ActionState | null>(null);

  const handleAprobar = async (loteId: string) => {
    try {
      await aprobarLote.mutateAsync(loteId);
      setActionState({ type: 'success', message: 'Lote aprobado. Los mensajes se están enviando.' });
    } catch {
      setActionState({ type: 'error', message: 'Error al aprobar el lote. Intentá nuevamente.' });
    }
  };

  const handleCancelar = async (loteId: string) => {
    try {
      await cancelarLote.mutateAsync(loteId);
      setActionState({ type: 'success', message: 'Lote rechazado correctamente.' });
    } catch {
      setActionState({ type: 'error', message: 'Error al rechazar el lote. Intentá nuevamente.' });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
            Aprobar Comunicaciones
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
            Lotes de envío masivo pendientes de aprobación.
          </p>
        </div>
      </div>

      {actionState && (
        <div
          className={`flex items-center gap-2 rounded-lg px-4 py-3 text-body-sm ${
            actionState.type === 'success'
              ? 'bg-success/10 text-success'
              : 'bg-error/10 text-error'
          }`}
        >
          <span className="material-symbols-outlined text-[18px]">
            {actionState.type === 'success' ? 'check_circle' : 'error'}
          </span>
          {actionState.message}
          <button
            type="button"
            onClick={() => setActionState(null)}
            className="ml-auto text-current opacity-60 hover:opacity-100"
          >
            <span className="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>
      )}

      {isLoading ? (
        <LoadingState rows={4} cols={5} />
      ) : isError ? (
        <EmptyState message="Error al cargar los lotes pendientes" icon="error" />
      ) : !data || data.items.length === 0 ? (
        <EmptyState message="No hay comunicaciones pendientes de aprobación" icon="approval" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Remitente</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Asunto</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Destinatarios</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Fecha</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((lote) => (
                <tr
                  key={lote.lote_id}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  <td className="px-4 py-3 text-body-sm text-on-surface">{lote.docente_nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface">{lote.asunto}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{lote.total_destinatarios}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">
                    {new Date(lote.created_at).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setPreviewLote(lote)}
                        className="inline-flex items-center gap-1 rounded-lg bg-surface-container-low px-2.5 py-1 text-label-xs font-medium text-on-surface-variant transition-colors hover:bg-surface-container"
                      >
                        <span className="material-symbols-outlined text-[14px]">preview</span>
                        Ver preview
                      </button>
                      <button
                        type="button"
                        onClick={() => setAprobarConfirmLote(lote)}
                        disabled={aprobarLote.isPending || cancelarLote.isPending}
                        className="inline-flex items-center gap-1 rounded-lg bg-success/10 px-2.5 py-1 text-label-xs font-medium text-success transition-colors hover:bg-success/20 disabled:opacity-50"
                      >
                        <span className="material-symbols-outlined text-[14px]">check_circle</span>
                        Aprobar
                      </button>
                      <button
                        type="button"
                        onClick={() => setCancelarConfirmLote(lote)}
                        disabled={aprobarLote.isPending || cancelarLote.isPending}
                        className="inline-flex items-center gap-1 rounded-lg bg-error/10 px-2.5 py-1 text-label-xs font-medium text-error transition-colors hover:bg-error/20 disabled:opacity-50"
                      >
                        <span className="material-symbols-outlined text-[14px]">cancel</span>
                        Rechazar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {previewLote && (
        <PreviewComunicacionModal
          isOpen={true}
          onClose={() => setPreviewLote(null)}
          onConfirm={() => setPreviewLote(null)}
          asunto={previewLote.asunto}
          cuerpo={previewLote.cuerpo}
          destinatarios={toLotePreviewDestinatarios(previewLote)}
        />
      )}

      <ConfirmDialog
        isOpen={!!aprobarConfirmLote}
        onClose={() => setAprobarConfirmLote(null)}
        onConfirm={() => {
          if (aprobarConfirmLote) handleAprobar(aprobarConfirmLote.lote_id);
        }}
        title="Aprobar lote de comunicaciones"
        message={`¿Confirmás la aprobación del lote de ${aprobarConfirmLote?.total_destinatarios ?? 0} destinatario(s)? Los mensajes pasarán a enviarse inmediatamente.`}
        confirmLabel="Aprobar"
        variant="info"
      />

      <ConfirmDialog
        isOpen={!!cancelarConfirmLote}
        onClose={() => setCancelarConfirmLote(null)}
        onConfirm={() => {
          if (cancelarConfirmLote) handleCancelar(cancelarConfirmLote.lote_id);
        }}
        title="Rechazar lote de comunicaciones"
        message={`¿Rechazás el envío del lote de ${cancelarConfirmLote?.total_destinatarios ?? 0} destinatario(s)? Esta acción es irreversible.`}
        confirmLabel="Rechazar"
        variant="danger"
      />
    </div>
  );
}
