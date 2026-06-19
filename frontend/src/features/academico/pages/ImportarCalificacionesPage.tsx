import { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { FileUploadArea } from '../components/FileUploadArea';
import { ActivityPreviewTable } from '../components/ActivityPreviewTable';
import { ThresholdInput } from '../components/ThresholdInput';
import { useFileUpload } from '../hooks/useFileUpload';
import { useUploadCalificaciones, useConfirmarImportacion, useConfigurarUmbral } from '../hooks/useImportarCalificaciones';
import { Button } from '@/shared/components/ds';
import type { ImportPreviewResponse } from '../types';

export function ImportarCalificacionesPage() {
  const { id: materiaId } = useParams<{ id: string }>();
  const { file, error: fileError, handleFileSelect, reset: resetFile } = useFileUpload();

  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [threshold, setThreshold] = useState(60);
  const [selectedActivityIds, setSelectedActivityIds] = useState<Set<string>>(new Set());

  const uploadMutation = useUploadCalificaciones(materiaId!);
  const confirmMutation = useConfirmarImportacion(materiaId!);
  const umbralMutation = useConfigurarUmbral(materiaId!);

  const handleUpload = useCallback(async () => {
    if (!file || !materiaId) return;
    try {
      const result = await uploadMutation.mutateAsync(file);
      setPreview(result);
      setSelectedActivityIds(new Set(result.actividades.map((a) => a.id)));
    } catch {
      // Error is handled via mutation state
    }
  }, [file, materiaId, uploadMutation]);

  const toggleActivity = useCallback((id: string) => {
    setSelectedActivityIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const handleConfirm = useCallback(async () => {
    if (!materiaId) return;
    await confirmMutation.mutateAsync(Array.from(selectedActivityIds));
  }, [materiaId, selectedActivityIds, confirmMutation]);

  const handleSaveThreshold = useCallback(async () => {
    if (!materiaId) return;
    await umbralMutation.mutateAsync(threshold);
  }, [materiaId, threshold, umbralMutation]);

  const handleReset = useCallback(() => {
    resetFile();
    setPreview(null);
    setThreshold(60);
    setSelectedActivityIds(new Set());
  }, [resetFile]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Importar Calificaciones</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Subí un archivo CSV o XLSX exportado desde el LMS para importar las calificaciones.
          </p>
        </div>
      </div>

      {!preview ? (
        <div className="space-y-4">
          <FileUploadArea
            onFileSelect={handleFileSelect}
            error={fileError}
            isLoading={uploadMutation.isPending}
          />
          {file && !fileError && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 14, color: 'var(--on-surface)' }}>{file.name}</span>
              <Button
                type="button"
                variant="primary"
                size="sm"
                icon="upload"
                onClick={handleUpload}
                disabled={uploadMutation.isPending}
              >
                {uploadMutation.isPending ? 'Analizando…' : 'Analizar archivo'}
              </Button>
              {uploadMutation.isError && (
                <span style={{ fontSize: 13, color: 'var(--error)' }}>
                  {uploadMutation.error?.message || 'Error al subir el archivo'}
                </span>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline mb-4">Actividades Detectadas</h3>
            <p className="text-body-sm text-on-surface-variant mb-4">
              Se detectaron {preview.alumnos_count} alumnos y {preview.calificaciones_count} calificaciones.
              Seleccioná las actividades a incluir en el análisis.
            </p>
            <ActivityPreviewTable
              actividades={preview.actividades.map((a) => ({
                ...a,
                selected: selectedActivityIds.has(a.id),
              }))}
              onToggle={toggleActivity}
            />
          </div>

          <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline mb-4">Configuración de Umbral</h3>
            <ThresholdInput
              value={threshold}
              onChange={setThreshold}
              onSave={handleSaveThreshold}
              disabled={umbralMutation.isPending}
            />
            {umbralMutation.isSuccess && (
              <p className="text-label-sm text-success mt-2">Umbral guardado correctamente</p>
            )}
            {umbralMutation.isError && (
              <p className="text-label-sm text-error mt-2">
                {umbralMutation.error?.message || 'Error al guardar el umbral'}
              </p>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button
              type="button"
              variant="primary"
              icon="check_circle"
              onClick={handleConfirm}
              disabled={selectedActivityIds.size === 0 || confirmMutation.isPending}
            >
              {confirmMutation.isPending ? 'Importando…' : 'Confirmar importación'}
            </Button>
            <Button type="button" variant="secondary" onClick={handleReset}>
              Cancelar
            </Button>
          </div>

          {confirmMutation.isSuccess && (
            <p style={{ fontSize: 13, color: 'var(--tertiary)' }}>Importación confirmada correctamente</p>
          )}
          {confirmMutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>
              {confirmMutation.error?.message || 'Error al confirmar la importación'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
