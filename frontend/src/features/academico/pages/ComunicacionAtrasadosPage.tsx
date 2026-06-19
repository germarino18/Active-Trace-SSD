import { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { StudentMultiSelect } from '../components/StudentMultiSelect';
import { PreviewComunicacionModal } from '../components/PreviewComunicacionModal';
import { TablaStatusComunicacion } from '../components/TablaStatusComunicacion';
import { useAtrasados } from '../hooks/useAtrasados';
import { usePreviewComunicacion, useEnviarComunicacion, useStatusComunicacion } from '../hooks/useComunicacion';
import { Button } from '@/shared/components/ds';

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

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button
              type="button"
              variant="primary"
              icon="preview"
              onClick={handlePreview}
              disabled={!hasSelection || previewMutation.isPending}
            >
              {previewMutation.isPending ? 'Generando vista previa…' : 'Vista previa'}
            </Button>
            <span style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>
              {hasSelection
                ? `${selectedIds.size} alumno${selectedIds.size !== 1 ? 's' : ''} seleccionado${selectedIds.size !== 1 ? 's' : ''}`
                : 'Seleccioná al menos un alumno'}
            </span>
          </div>

          {previewMutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>
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
            <p style={{ fontSize: 13, color: 'var(--tertiary)' }}>Comunicación enviada a la cola de despacho</p>
          )}

          {enviarMutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>
              {enviarMutation.error?.message || 'Error al enviar la comunicación'}
            </p>
          )}
        </>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ background: 'color-mix(in srgb, var(--tertiary) 10%, transparent)', border: '1px solid color-mix(in srgb, var(--tertiary) 30%, transparent)', borderRadius: 'var(--radius-lg)', padding: 20 }}>
            <p style={{ margin: 0, fontSize: 15, fontWeight: 600, color: 'var(--tertiary)' }}>
              Comunicación enviada a la cola de despacho
            </p>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>
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
