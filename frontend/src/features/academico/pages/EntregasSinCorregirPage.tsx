import { useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { FileUploadArea } from '../components/FileUploadArea';
import { TablaEntregasPendientes } from '../components/TablaEntregasPendientes';
import { useFileUpload } from '../hooks/useFileUpload';
import { useDetectarEntregas, useExportarEntregas } from '../hooks/useEntregas';

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
            <div className="flex items-center gap-3">
              <span className="text-label-md text-on-surface">{file.name}</span>
              <button
                type="button"
                onClick={handleUpload}
                disabled={detectMutation.isPending}
                className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
              >
                {detectMutation.isPending ? 'Analizando...' : 'Detectar entregas'}
              </button>
            </div>
          )}
          {detectMutation.isError && (
            <p className="text-label-sm text-error">
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
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleExport}
              disabled={exportMutation.isPending}
              className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[18px]">download</span>
              {exportMutation.isPending ? 'Exportando...' : 'Exportar'}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
            >
              Nuevo análisis
            </button>
          </div>
          {exportMutation.isError && (
            <p className="text-label-sm text-error">
              {exportMutation.error?.message || 'Error al exportar'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
