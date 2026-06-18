import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useMisEquipos } from '../hooks/useEquipos';
import { DataTable, type ColumnDef } from '../components/DataTable';
import { Spinner } from '@/shared/components/Spinner';
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

export function MisEquiposPage() {
  const { session, hasAnyPermission } = useAuth();
  const navigate = useNavigate();
  const { data, isLoading, error } = useMisEquipos();

  if (session.status !== 'authenticated') return null;

  if (!hasAnyPermission(['PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR', 'ADMIN'])) {
    return (
      <EmptyState
        message="No tenés acceso a esta sección"
        icon="lock"
      />
    );
  }

  const handleExport = async () => {
    try {
      const blob = await equiposService.exportarEquipo();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'mis-equipos.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      // Silently fail — the user will see nothing happened
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return <EmptyState message="Error al cargar tus asignaciones" icon="error" />;
  }

  const asignaciones = data?.asignaciones ?? [];

  if (asignaciones.length === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Mis Equipos</h2>
            <p className="text-body-md text-on-surface-variant mt-1">Tus asignaciones docentes activas</p>
          </div>
        </div>
        <EmptyState message="No tenés asignaciones activas" icon="assignment" />
      </div>
    );
  }

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
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Mis Equipos</h2>
          <p className="text-body-md text-on-surface-variant mt-1">Tus asignaciones docentes activas</p>
        </div>
        <button
          type="button"
          onClick={handleExport}
          className="flex items-center gap-1.5 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
        >
          <span className="material-symbols-outlined text-[18px]">download</span>
          Exportar
        </button>
      </div>

      <DataTable
        columns={columns}
        data={asignaciones}
        rowKey="id"
        emptyMessage="No tenés asignaciones activas"
      />
    </div>
  );
}
