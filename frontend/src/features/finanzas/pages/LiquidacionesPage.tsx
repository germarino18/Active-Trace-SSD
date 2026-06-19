import { useState, useCallback } from 'react';
import { useLiquidacion, useLiquidacionKPIs, useCerrarLiquidacion, useHistorial } from '../hooks/useLiquidaciones';
import { LiquidacionKPIs } from '../components/LiquidacionKPIs';
import { LiquidacionTable } from '../components/LiquidacionTable';
import { CerrarLiquidacionModal } from '../components/CerrarLiquidacionModal';
import { HistorialSection } from '../components/HistorialSection';
import { HelpButton } from '@/features/coordinacion/components/HelpButton';
import type { SegmentoLiquidacion } from '../types/liquidaciones';
import { Button } from '@/shared/components/ds';

const segmentos: { key: SegmentoLiquidacion; label: string }[] = [
  { key: 'general', label: 'General' },
  { key: 'nexo', label: 'NEXO' },
  { key: 'factura', label: 'Factura' },
];

const currentPeriod = '2025-01';

export function LiquidacionesPage() {
  const [activeSegmento, setActiveSegmento] = useState<SegmentoLiquidacion>('general');
  const [showCerrarModal, setShowCerrarModal] = useState(false);

  const liquidacionFilters = { periodo: currentPeriod, segmento: activeSegmento };

  const { data: liquidacion, isLoading: isLoadingLiquidacion } = useLiquidacion(liquidacionFilters);
  const { data: kpis, isLoading: isLoadingKPIs } = useLiquidacionKPIs(currentPeriod);
  const { data: historial, isLoading: isLoadingHistorial } = useHistorial();
  const cerrarMutation = useCerrarLiquidacion();

  const handleCerrarLiquidacion = useCallback(async () => {
    await cerrarMutation.mutateAsync({ periodo: currentPeriod });
  }, [cerrarMutation]);

  const handleExportar = useCallback(async () => {
    const { exportarLiquidacion } = await import('../services/liquidaciones.service');
    try {
      const blob = await exportarLiquidacion(currentPeriod);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `liquidacion-${currentPeriod}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      // Silently fail
    }
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Liquidaciones</h2>
            <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
              Gestioná las liquidaciones del período {currentPeriod}
            </p>
          </div>
          <HelpButton tooltip="Administrá las liquidaciones docentes del período activo. Usá las pestañas para cambiar entre vista General, NEXO y Factura." />
        </div>
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="secondary"
            icon="download"
            onClick={handleExportar}
          >
            Exportar
          </Button>
          {liquidacion && !liquidacion.cerrada && (
            <Button
              type="button"
              variant="secondary"
              icon="lock"
              onClick={() => setShowCerrarModal(true)}
            >
              Cerrar liquidación
            </Button>
          )}
        </div>
      </div>

      <div className="border-b border-outline-variant">
        <nav className="flex gap-0" role="tablist">
          {segmentos.map((seg) => (
            <button
              key={seg.key}
              type="button"
              role="tab"
              aria-selected={activeSegmento === seg.key}
              onClick={() => setActiveSegmento(seg.key)}
              className={`px-4 py-2.5 text-label-sm font-medium transition-colors border-b-2 ${
                activeSegmento === seg.key
                  ? 'border-primary text-primary'
                  : 'border-transparent text-on-surface-variant hover:text-on-surface hover:border-outline-variant'
              }`}
            >
              {seg.label}
            </button>
          ))}
        </nav>
      </div>

      <LiquidacionKPIs
        kpis={kpis ?? { total_docentes: 0, monto_total: 0, facturas_pendientes: 0, periodos_cerrados: 0 }}
        isLoading={isLoadingKPIs}
      />

      <LiquidacionTable
        liquidacion={liquidacion}
        isLoading={isLoadingLiquidacion}
      />

      <HistorialSection
        items={historial}
        isLoading={isLoadingHistorial}
      />

      <CerrarLiquidacionModal
        isOpen={showCerrarModal}
        onClose={() => setShowCerrarModal(false)}
        onConfirm={handleCerrarLiquidacion}
        periodo={currentPeriod}
        totalDocentes={liquidacion?.total_docentes ?? 0}
        montoTotal={liquidacion?.monto_total ?? 0}
      />
    </div>
  );
}
