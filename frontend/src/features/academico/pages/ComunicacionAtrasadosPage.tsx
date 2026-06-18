import { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { StudentMultiSelect } from '../components/StudentMultiSelect';
import { PreviewComunicacionModal } from '../components/PreviewComunicacionModal';
import { TablaStatusComunicacion } from '../components/TablaStatusComunicacion';
import { useAtrasados } from '../hooks/useAtrasados';
import { usePreviewComunicacion, useEnviarComunicacion, useStatusComunicacion } from '../hooks/useComunicacion';

export function ComunicacionAtrasadosPage() {
  const { id: materiaId } = useParams<{ id: string }>();
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [showPreview, setShowPreview] = useState(false);
  const [comunicacionId, setComunicacionId] = useState<string | null>(null);

  const { data: atrasadosData, isLoading: loadingAtrasados } = useAtrasados(materiaId!);
  const previewMutation = usePreviewComunicacion(materiaId!);
  const enviarMutation = useEnviarComunicacion();
  const { data: statusData } = useStatusComunicacion(comunicacionId);

  const toggleStudent = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handlePreview = useCallback(async () => {
    if (selectedIds.size === 0) return;
    try {
      await previewMutation.mutateAsync(Array.from(selectedIds));
      setShowPreview(true);
    } catch {
      // Error handled via mutation state
    }
  }, [selectedIds, previewMutation]);

  const handleSend = useCallback(async () => {
    if (!materiaId || selectedIds.size === 0) return;
    try {
      const result = await enviarMutation.mutateAsync({
        materiaId,
        studentIds: Array.from(selectedIds),
      });
      setComunicacionId(result.comunicacion_id);
      setShowPreview(false);
      setSelectedIds(new Set());
    } catch {
      // Error handled via mutation state
    }
  }, [materiaId, selectedIds, enviarMutation]);

  const handleClosePreview = useCallback(() => {
    if (!enviarMutation.isPending) {
      setShowPreview(false);
    }
  }, [enviarMutation.isPending]);

  const hasSelection = selectedIds.size > 0;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Comunicar a Atrasados</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Seleccioná los alumnos atrasados y enviáles una comunicación personalizada.
        </p>
      </div>

      {!comunicacionId ? (
        <>
          <StudentMultiSelect
            students={atrasadosData?.alumnos}
            selectedIds={selectedIds}
            onToggle={toggleStudent}
            isLoading={loadingAtrasados}
          />

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handlePreview}
              disabled={!hasSelection || previewMutation.isPending}
              className="rounded-lg bg-primary px-4 py-2 text-label-md font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              {previewMutation.isPending ? 'Generando vista previa...' : 'Vista previa'}
            </button>
            <p className="text-label-sm text-on-surface-variant">
              {hasSelection
                ? `${selectedIds.size} alumno(s) seleccionados`
                : 'Seleccioná al menos un alumno'}
            </p>
          </div>

          {previewMutation.isError && (
            <p className="text-label-sm text-error">
              {previewMutation.error?.message || 'Error al generar la vista previa'}
            </p>
          )}

          {previewMutation.data && (
            <PreviewComunicacionModal
              isOpen={showPreview}
              onClose={handleClosePreview}
              onConfirm={handleSend}
              asunto={previewMutation.data.asunto}
              cuerpo={previewMutation.data.cuerpo}
              destinatarios={previewMutation.data.destinatarios}
              isSending={enviarMutation.isPending}
            />
          )}

          {enviarMutation.isSuccess && (
            <p className="text-label-sm text-success">
              Comunicación enviada a la cola de despacho
            </p>
          )}

          {enviarMutation.isError && (
            <p className="text-label-sm text-error">
              {enviarMutation.error?.message || 'Error al enviar la comunicación'}
            </p>
          )}
        </>
      ) : (
        <div className="space-y-4">
          <div className="rounded-xl border border-outline-variant bg-success/5 p-md">
            <p className="text-body-md font-medium text-success">
              Comunicación enviada a la cola de despacho
            </p>
            <p className="text-label-sm text-on-surface-variant mt-1">
              ID: {comunicacionId}
            </p>
          </div>

          <TablaStatusComunicacion
            mensajes={statusData?.mensajes}
            isLoading={!statusData}
            isTerminal={statusData?.terminal}
          />
        </div>
      )}
    </div>
  );
}
