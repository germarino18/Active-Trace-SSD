import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { TablaAtrasados } from '../components/TablaAtrasados';
import { TablaRanking } from '../components/TablaRanking';
import { TablaNotasFinales } from '../components/TablaNotasFinales';
import { ReportesRapidos } from '../components/ReportesRapidos';
import { useAtrasados, useRanking, useNotasFinales, useReportesRapidos } from '../hooks/useAtrasados';
import { Tabs } from '@/shared/components/ds';

const subTabs = [
  { id: 'atrasados', label: 'Atrasados' },
  { id: 'ranking', label: 'Ranking' },
  { id: 'notas-finales', label: 'Notas Finales' },
  { id: 'reportes', label: 'Reportes' },
] as const;

type SubTab = (typeof subTabs)[number]['id'];

export function VistaAtrasadosPage() {
  const { id: materiaId } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<SubTab>('atrasados');

  const { data: atrasadosData, isLoading: loadingAtrasados } = useAtrasados(materiaId!);
  const { data: rankingData, isLoading: loadingRanking } = useRanking(materiaId!);
  const { data: notasData, isLoading: loadingNotas } = useNotasFinales(materiaId!);
  const { data: reportesData, isLoading: loadingReportes } = useReportesRapidos(materiaId!);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Alumnos Atrasados</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Visualizá los alumnos con actividades pendientes o por debajo del umbral.
        </p>
      </div>

      <Tabs
        tabs={subTabs.map((t) => ({ id: t.id, label: t.label }))}
        value={activeTab}
        onChange={(id) => setActiveTab(id as SubTab)}
      />

      {activeTab === 'atrasados' && (
        <TablaAtrasados
          data={atrasadosData?.alumnos}
          isLoading={loadingAtrasados}
          umbral={atrasadosData?.umbral}
        />
      )}
      {activeTab === 'ranking' && (
        <TablaRanking
          data={rankingData?.alumnos}
          isLoading={loadingRanking}
        />
      )}
      {activeTab === 'notas-finales' && (
        <TablaNotasFinales
          data={notasData?.alumnos}
          isLoading={loadingNotas}
        />
      )}
      {activeTab === 'reportes' && (
        <ReportesRapidos
          data={reportesData}
          isLoading={loadingReportes}
        />
      )}
    </div>
  );
}
