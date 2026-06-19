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
import { Button } from '@/shared/components/ds';

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
            <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Equipos Docentes</h2>
            <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
              Gestioná las asignaciones del cuerpo docente
            </p>
          </div>
          <HelpButton tooltip="Administrá las asignaciones de profesores, tutores y nexos a las materias. Usá los filtros para encontrar asignaciones específicas." />
        </div>
        {canManage && (
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="primary"
              icon="add"
              onClick={() => navigate('/coordinacion/equipos/nuevo')}
            >
              Nueva asignación
            </Button>
            <Button
              type="button"
              variant="secondary"
              icon="group_add"
              onClick={() => navigate('/coordinacion/equipos/asignacion-masiva')}
            >
              Asignación masiva
            </Button>
            <Button
              type="button"
              variant="secondary"
              icon="content_copy"
              onClick={() => navigate('/coordinacion/equipos/clonar')}
            >
              Clonar equipo
            </Button>
            <Button
              type="button"
              variant="secondary"
              icon="calendar_month"
              onClick={() => navigate('/coordinacion/equipos/vigencia')}
            >
              Modificar vigencia
            </Button>
            <Button
              type="button"
              variant="secondary"
              icon="download"
              onClick={handleExport}
            >
              Exportar
            </Button>
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
