import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useEquipos, useEliminarAsignacion } from '../hooks/useEquipos';
import { DataTable, type ColumnDef } from '../components/DataTable';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Asignacion } from '../types';

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

export function EquipoDetallePage() {
  const { id } = useParams<{ id: string }>();
  const { hasAnyPermission } = useAuth();
  const navigate = useNavigate();
  const { data, isLoading } = useEquipos({ usuario: id });
  const deleteMutation = useEliminarAsignacion();
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const canManage = hasAnyPermission(['COORDINADOR', 'ADMIN']);

  if (!id) {
    return <EmptyState message="ID de equipo no especificado" icon="error" />;
  }

  const columns: ColumnDef<Asignacion>[] = [
    {
      key: 'docente',
      label: 'Docente',
      render: (row) => `${row.docente.apellido}, ${row.docente.nombre}`,
    },
    {
      key: 'email',
      label: 'Email',
      render: (row) => row.docente.email,
    },
    {
      key: 'materia_nombre',
      label: 'Materia',
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => navigate('/coordinacion/equipos')}
            className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low"
          >
            <span className="material-symbols-outlined text-[20px]">arrow_back</span>
          </button>
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">
              {data?.asignaciones?.[0]?.materia_nombre ?? 'Detalle del equipo'}
            </h2>
            <p className="text-body-md text-on-surface-variant mt-1">
              {data?.asignaciones?.[0]?.carrera_nombre} — Cohorte{' '}
              {data?.asignaciones?.[0]?.cohorte_nombre}
            </p>
          </div>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={data?.asignaciones ?? []}
        rowKey="id"
        isLoading={isLoading}
        emptyMessage="No hay miembros en este equipo"
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) {
            deleteMutation.mutate(deleteTarget);
          }
        }}
        title="Eliminar asignación"
        message="¿Estás seguro de que querés eliminar esta asignación?"
        confirmLabel="Eliminar"
        variant="danger"
      />
    </div>
  );
}
