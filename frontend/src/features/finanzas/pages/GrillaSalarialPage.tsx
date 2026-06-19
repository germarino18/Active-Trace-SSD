import { useState, useCallback } from 'react';
import { useSalariosBase, usePlus, useCrearSalarioBase, useEditarSalarioBase, useCrearPlus, useEditarPlus } from '../hooks/useGrillaSalarial';
import { SalarioBaseTable } from '../components/SalarioBaseTable';
import { PlusTable } from '../components/PlusTable';
import { SalaryFormModal } from '../components/SalaryFormModal';
import { HelpButton } from '@/features/coordinacion/components/HelpButton';
import { useAuth } from '@/features/auth/hooks/useAuth';
import type { SalarioBase, PlusSalarial, SalarioBaseFormData, PlusFormData } from '../types/grilla-salarial';
import { Button } from '@/shared/components/ds';

type ActiveTab = 'salarios-base' | 'plus';

const tabs: { key: ActiveTab; label: string }[] = [
  { key: 'salarios-base', label: 'Salario Base' },
  { key: 'plus', label: 'Plus' },
];

export function GrillaSalarialPage() {
  const { hasPermission } = useAuth();
  const [activeTab, setActiveTab] = useState<ActiveTab>('salarios-base');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSalarioBase, setEditingSalarioBase] = useState<SalarioBase | undefined>();
  const [editingPlus, setEditingPlus] = useState<PlusSalarial | undefined>();

  const { data: salariosBase, isLoading: loadingSalariosBase } = useSalariosBase();
  const { data: plus, isLoading: loadingPlus } = usePlus();
  const crearSalarioBase = useCrearSalarioBase();
  const editarSalarioBase = useEditarSalarioBase();
  const crearPlus = useCrearPlus();
  const editarPlus = useEditarPlus();

  const canEdit = hasPermission('finanzas:grilla:gestionar');

  const handleCreate = useCallback(() => {
    setEditingSalarioBase(undefined);
    setEditingPlus(undefined);
    setModalOpen(true);
  }, []);

  const handleEditSalarioBase = useCallback((item: SalarioBase) => {
    setEditingSalarioBase(item);
    setEditingPlus(undefined);
    setModalOpen(true);
  }, []);

  const handleEditPlus = useCallback((item: PlusSalarial) => {
    setEditingPlus(item);
    setEditingSalarioBase(undefined);
    setModalOpen(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setModalOpen(false);
    setEditingSalarioBase(undefined);
    setEditingPlus(undefined);
  }, []);

  const handleSubmitSalarioBase = useCallback(
    async (data: SalarioBaseFormData | PlusFormData) => {
      if (editingSalarioBase) {
        await editarSalarioBase.mutateAsync({ id: editingSalarioBase.id, data: data as SalarioBaseFormData });
      } else {
        await crearSalarioBase.mutateAsync(data as SalarioBaseFormData);
      }
    },
    [editingSalarioBase, editarSalarioBase, crearSalarioBase],
  );

  const handleSubmitPlus = useCallback(
    async (data: SalarioBaseFormData | PlusFormData) => {
      if (editingPlus) {
        await editarPlus.mutateAsync({ id: editingPlus.id, data: data as PlusFormData });
      } else {
        await crearPlus.mutateAsync(data as PlusFormData);
      }
    },
    [editingPlus, editarPlus, crearPlus],
  );

  const isSalarioBaseMode = activeTab === 'salarios-base' || !!editingSalarioBase;
  const modalMode = isSalarioBaseMode ? 'salario-base' : 'plus';
  const handleSubmit = isSalarioBaseMode ? handleSubmitSalarioBase : handleSubmitPlus;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Grilla Salarial</h2>
            <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
              Gestioná los salarios base y plus por rol docente.
            </p>
          </div>
          <HelpButton tooltip="Configuración de la grilla salarial: salarios base por rol y plus adicionales con sus respectivas vigencias." />
        </div>
        {canEdit && (
          <Button
            type="button"
            variant="primary"
            icon="add"
            onClick={handleCreate}
          >
            {activeTab === 'salarios-base' ? 'Nuevo salario base' : 'Nuevo plus'}
          </Button>
        )}
      </div>

      <div className="border-b border-outline-variant">
        <nav className="flex gap-0" role="tablist">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2.5 text-label-sm font-medium transition-colors border-b-2 ${
                activeTab === tab.key
                  ? 'border-primary text-primary'
                  : 'border-transparent text-on-surface-variant hover:text-on-surface hover:border-outline-variant'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {activeTab === 'salarios-base' && (
        <SalarioBaseTable
          items={salariosBase}
          isLoading={loadingSalariosBase}
          onEdit={handleEditSalarioBase}
          canEdit={canEdit}
        />
      )}

      {activeTab === 'plus' && (
        <PlusTable
          items={plus}
          isLoading={loadingPlus}
          onEdit={handleEditPlus}
          canEdit={canEdit}
        />
      )}

      <SalaryFormModal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        onSubmit={handleSubmit}
        mode={modalMode}
        selectedItem={editingSalarioBase ?? editingPlus}
      />
    </div>
  );
}
