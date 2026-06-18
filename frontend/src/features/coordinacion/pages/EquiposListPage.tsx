import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useEquipos, useEliminarAsignacion } from '../hooks/useEquipos';
import { DataTable, type ColumnDef } from '../components/DataTable';
import { FilterBar, type FilterDefinition } from '../components/FilterBar';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { HelpButton } from '../components/HelpButton';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Asignacion } from '../types';
import * as equiposService from '../services/equipos.service';

const roleLabels: Record<string, string> = {
  PROFESOR: 'Profesor',
  TUTOR: 'Tutor',
  NEXO: 'Nexo',
  COORDINADOR: 'Coordinador',
};

const estadoBadge: Record<string, string> = {
  Activa: 'bg-success/10 text-success',
  Vencida: 'bg-warning/10 text-warning',
  Cancelada: 'bg-error/10 text-error',
};

const filterDefs: FilterDefinition[] = [
  { key: 'materia', label: 'Materia', type: 'text', placeholder: 'Buscar materia...' },
  { key: 'carrera', label: 'Carrera', type: 'text', placeholder: 'Buscar carrera...' },
  { key: 'cohorte', label: 'Cohorte', type: 'text', placeholder: 'Ej: 2024' },
  { key: 'usuario', label: 'Usuario', type: 'text', placeholder: 'Nombre o email...' },
  {
    key: 'rol',
    label: 'Rol',
    type: 'select',
    options: [
      { value: 'PROFESOR', label: 'Profesor' },
      { value: 'TUTOR', label: 'Tutor' },
      { value: 'NEXO', label: 'Nexo' },
      { value: 'COORDINADOR', label: 'Coordinador' },
    ],
  },
];

export function EquiposListPage() {
  const { hasAnyPermission } = useAuth();
  const navigate = useNavigate();
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const deleteMutation = useEliminarAsignacion();

  const appliedFilters = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v !== undefined && v !== ''),
  );

  const { data, isLoading } = useEquipos(
    Object.keys(appliedFilters).length > 0 ? appliedFilters : undefined,
  );

  const handleFilterChange = (key: string, value: unknown) => {
    setFilters((prev) => ({ ...prev, [key]: value as string }));
  };

  const handleClearFilters = () => {
    setFilters({});
  };

  const handleExport = async () => {
    try {
      const blob = await equiposService.exportarEquipo(appliedFilters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'equipos.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      // Silently fail
    }
  };

  const canManage = hasAnyPermission(['COORDINADOR', 'ADMIN']);
  const asignaciones = data?.asignaciones ?? [];

  const columns: ColumnDef<Asignacion>[] = [
    {
      key: 'materia_nombre',
      label: 'Materia',
      sortable: true,
      render: (row) => (
        <button
          type="button"
          onClick={() => navigate(`/equipos/${row.id}`)}
          className="text-primary hover:underline font-medium"
        >
          {row.materia_nombre}
        </button>
      ),
    },
    {
      key: 'carrera_nombre',
      label: 'Carrera',
      sortable: true,
    },
    {
      key: 'cohorte_nombre',
      label: 'Cohorte',
      sortable: true,
    },
    {
      key: 'docente',
      label: 'Docente',
      render: (row) => `${row.docente.apellido}, ${row.docente.nombre}`,
    },
    {
      key: 'rol',
      label: 'Rol',
      render: (row) => (
        <span className="inline-flex rounded-full bg-primary/10 px-2.5 py-0.5 text-label-xs font-medium text-primary">
          {roleLabels[row.rol] ?? row.rol}
        </span>
      ),
    },
    {
      key: 'vigencia_desde',
      label: 'Vigencia desde',
      render: (row) => new Date(row.vigencia_desde).toLocaleDateString('es-AR'),
    },
    {
      key: 'vigencia_hasta',
      label: 'Vigencia hasta',
      render: (row) => new Date(row.vigencia_hasta).toLocaleDateString('es-AR'),
    },
    {
      key: 'estado',
      label: 'Estado',
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-label-xs font-medium ${estadoBadge[row.estado] ?? ''}`}>
          {row.estado}
        </span>
      ),
    },
    ...(canManage
      ? [
          {
            key: 'acciones' as const,
            label: 'Acciones',
            render: (row: Asignacion) => (
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => navigate(`/coordinacion/equipos/editar/${row.id}`)}
                  className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                  title="Editar"
                >
                  <span className="material-symbols-outlined text-[18px]">edit</span>
                </button>
                <button
                  type="button"
                  onClick={() => setDeleteTarget(row.id)}
                  className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-error"
                  title="Eliminar"
                >
                  <span className="material-symbols-outlined text-[18px]">delete</span>
                </button>
              </div>
            ),
          },
        ]
      : []),
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Equipos Docentes</h2>
            <p className="text-body-md text-on-surface-variant mt-1">
              Gestioná las asignaciones del cuerpo docente
            </p>
          </div>
          <HelpButton tooltip="Administrá las asignaciones de profesores, tutores y nexos a las materias. Usá los filtros para encontrar asignaciones específicas." />
        </div>
        {canManage && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => navigate('/coordinacion/equipos/nuevo')}
              className="flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
            >
              <span className="material-symbols-outlined text-[18px]">add</span>
              Nueva asignación
            </button>
            <button
              type="button"
              onClick={() => navigate('/coordinacion/equipos/asignacion-masiva')}
              className="flex items-center gap-1.5 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
            >
              <span className="material-symbols-outlined text-[18px]">group_add</span>
              Asignación masiva
            </button>
            <button
              type="button"
              onClick={() => navigate('/coordinacion/equipos/clonar')}
              className="flex items-center gap-1.5 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
            >
              <span className="material-symbols-outlined text-[18px]">content_copy</span>
              Clonar equipo
            </button>
            <button
              type="button"
              onClick={() => navigate('/coordinacion/equipos/vigencia')}
              className="flex items-center gap-1.5 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
            >
              <span className="material-symbols-outlined text-[18px]">calendar_month</span>
              Modificar vigencia
            </button>
            <button
              type="button"
              onClick={handleExport}
              className="flex items-center gap-1.5 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
            >
              <span className="material-symbols-outlined text-[18px]">download</span>
              Exportar
            </button>
          </div>
        )}
      </div>

      <FilterBar
        filters={filterDefs}
        values={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      {!canManage ? (
        <DataTable
          columns={columns}
          data={asignaciones}
          rowKey="id"
          isLoading={isLoading}
          emptyMessage="No se encontraron equipos docentes"
        />
      ) : (
        <DataTable
          columns={columns}
          data={asignaciones}
          rowKey="id"
          isLoading={isLoading}
          emptyMessage="No se encontraron equipos docentes"
        />
      )}

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) {
            deleteMutation.mutate(deleteTarget);
          }
        }}
        title="Eliminar asignación"
        message="¿Estás seguro de que querés eliminar esta asignación docente?"
        confirmLabel="Eliminar"
        variant="danger"
        cascadeWarning="Esta acción eliminará la asignación de forma permanente. Los docentes afectados perderán acceso a la materia."
      />
    </div>
  );
}
