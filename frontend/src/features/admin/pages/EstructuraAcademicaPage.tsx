import { useState } from 'react';
import { CarrerasPage } from './CarrerasPage';
import { CohortesPage } from './CohortesPage';
import { MateriasPage } from './MateriasPage';
import { Tabs } from '@/shared/components/ds';

const TABS = [
  { id: 'carreras', label: 'Carreras', icon: 'school' },
  { id: 'cohortes', label: 'Cohortes', icon: 'calendar_view_month' },
  { id: 'materias', label: 'Materias', icon: 'menu_book' },
];

type TabKey = 'carreras' | 'cohortes' | 'materias';

export function EstructuraAcademicaPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('carreras');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          Estructura Académica
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Gestioná carreras, cohortes y materias del plan académico
        </p>
      </div>

      <Tabs tabs={TABS} value={activeTab} onChange={(id) => setActiveTab(id as TabKey)} />

      {activeTab === 'carreras' && <CarrerasPage />}
      {activeTab === 'cohortes' && <CohortesPage />}
      {activeTab === 'materias' && <MateriasPage />}
    </div>
  );
}
