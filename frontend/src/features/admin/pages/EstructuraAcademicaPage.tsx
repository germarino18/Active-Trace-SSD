import { useState } from 'react';
import { CarrerasPage } from './CarrerasPage';
import { CohortesPage } from './CohortesPage';
import { MateriasPage } from './MateriasPage';

const tabs = [
  { key: 'carreras', label: 'Carreras' },
  { key: 'cohortes', label: 'Cohortes' },
  { key: 'materias', label: 'Materias' },
] as const;

type TabKey = (typeof tabs)[number]['key'];

export function EstructuraAcademicaPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('carreras');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">
          Estructura Académica
        </h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Gestioná carreras, cohortes y materias del plan académico
        </p>
      </div>

      <div className="flex gap-1 rounded-xl bg-surface-container-low p-1" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            role="tab"
            aria-selected={activeTab === tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 rounded-lg px-4 py-2 text-label-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-surface text-on-surface shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'carreras' && <CarrerasPage />}
      {activeTab === 'cohortes' && <CohortesPage />}
      {activeTab === 'materias' && <MateriasPage />}
    </div>
  );
}
