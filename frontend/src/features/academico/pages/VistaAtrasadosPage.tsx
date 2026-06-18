import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { TablaAtrasados } from '../components/TablaAtrasados';
import { TablaRanking } from '../components/TablaRanking';
import { TablaNotasFinales } from '../components/TablaNotasFinales';
import { ReportesRapidos } from '../components/ReportesRapidos';
import { useAtrasados, useRanking, useNotasFinales, useReportesRapidos } from '../hooks/useAtrasados';

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
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Alumnos Atrasados</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Visualizá los alumnos con actividades pendientes o por debajo del umbral.
        </p>
      </div>

      <div className="border-b border-outline-variant">
        <nav className="flex gap-4 -mb-px">
          {subTabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-label-md font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-on-surface-variant hover:text-on-surface hover:border-outline-variant'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

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
