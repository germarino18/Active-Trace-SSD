import { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { FileUploadArea } from '../components/FileUploadArea';
import { TablaEntregasPendientes } from '../components/TablaEntregasPendientes';
import { useFileUpload } from '../hooks/useFileUpload';
import { useDetectarEntregas, useExportarEntregas } from '../hooks/useEntregas';
import { Button } from '@/shared/components/ds';

export function EntregasSinCorregirPage() {
  const { id: materiaId } = useParams<{ id: string }>();
  const { file, error: fileError, handleFileSelect, reset: resetFile } = useFileUpload();
  const [showResults, setShowResults] = useState(false);

  const detectMutation = useDetectarEntregas(materiaId!);
  const exportMutation = useExportarEntregas();

  const handleUpload = useCallback(async () => {
    if (!file || !materiaId) return;
    try {
      await detectMutation.mutateAsync(file);
      setShowResults(true);
    } catch {
      // Error is handled via mutation state
    }
  }, [file, materiaId, detectMutation]);

  const handleExport = useCallback(async () => {
    if (!materiaId) return;
    await exportMutation.mutateAsync(materiaId);
  }, [materiaId, exportMutation]);

  const handleReset = useCallback(() => {
    resetFile();
    setShowResults(false);
  }, [resetFile]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Entregas Sin Corregir</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Subí un reporte de completitud para detectar actividades entregadas pero no corregidas.
        </p>
      </div>

      {!showResults ? (
        <div className="space-y-4">
          <FileUploadArea
            onFileSelect={handleFileSelect}
            error={fileError}
            isLoading={detectMutation.isPending}
          />
          {file && !fileError && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span style={{ fontSize: 14, color: 'var(--on-surface)' }}>{file.name}</span>
              <Button
                type="button"
                variant="primary"
                size="sm"
                icon="search"
                onClick={handleUpload}
                disabled={detectMutation.isPending}
              >
                {detectMutation.isPending ? 'Analizando…' : 'Detectar entregas'}
              </Button>
            </div>
          )}
          {detectMutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>
              {detectMutation.error?.message || 'Error al detectar entregas'}
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <TablaEntregasPendientes
            data={detectMutation.data?.entregas}
            isLoading={detectMutation.isPending}
          />
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Button
              type="button"
              variant="primary"
              icon="download"
              onClick={handleExport}
              disabled={exportMutation.isPending}
            >
              {exportMutation.isPending ? 'Exportando…' : 'Exportar'}
            </Button>
            <Button type="button" variant="secondary" onClick={handleReset}>
              Nuevo análisis
            </Button>
          </div>
          {exportMutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>
              {exportMutation.error?.message || 'Error al exportar'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
