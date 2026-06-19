import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useProgramas, useEliminarPrograma } from '../hooks/useProgramas';
import { DataTable, type ColumnDef } from '../components/DataTable';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { HelpButton } from '../components/HelpButton';
import { useAuth } from '@/features/auth/hooks/useAuth';
import type { ProgramaMateria } from '../types';
import { Button } from '@/shared/components/ds';

export function ProgramasListPage() {
  const navigate = useNavigate();
  const { hasPermission } = useAuth();
  const { data, isLoading } = useProgramas();
  const eliminarPrograma = useEliminarPrograma();
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);

  const canManage = hasPermission('coordinacion:programas:gestionar');

  const columns: ColumnDef<ProgramaMateria>[] = [
    { key: 'titulo', label: 'Título' },
    { key: 'materia_nombre', label: 'Materia' },
    { key: 'carrera_nombre', label: 'Carrera' },
    { key: 'cohorte_nombre', label: 'Cohorte' },
    {
      key: 'archivo_url',
      label: 'Archivo',
      render: (row) => (
        <a
          href={row.archivo_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-2.5 py-1 text-label-xs font-medium text-primary hover:bg-primary/20 transition-colors"
        >
          <span className="material-symbols-outlined text-[14px]">download</span>
          Descargar
        </a>
      ),
    },
    {
      key: 'fecha_subida',
      label: 'Fecha de subida',
      render: (row) => new Date(row.fecha_subida).toLocaleDateString('es-AR'),
    },
    ...(canManage
      ? [
          {
            key: 'acciones' as const,
            label: 'Acciones',
            render: (row: ProgramaMateria) => (
              <button
                type="button"
                onClick={() => setDeleteTarget(row.id)}
                className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-error"
                title="Eliminar"
              >
                <span className="material-symbols-outlined text-[18px]">delete</span>
              </button>
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
            <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Programas</h2>
            <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
              Gestioná los programas de estudio subidos por materia.
            </p>
          </div>
          <HelpButton tooltip="Listado de programas de estudio cargados en el sistema. Podés descargar o eliminar cada programa." />
        </div>
        {canManage && (
          <Button
            type="button"
            variant="primary"
            icon="upload_file"
            onClick={() => navigate('/programas/nuevo')}
          >
            Subir programa
          </Button>
        )}
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        rowKey="id"
        isLoading={isLoading}
        emptyMessage="No hay programas de estudio cargados."
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) {
            eliminarPrograma.mutate(deleteTarget);
          }
        }}
        title="Eliminar programa"
        message="¿Estás seguro de que querés eliminar este programa de estudio?"
        confirmLabel="Eliminar"
        variant="danger"
        cascadeWarning="Esta acción eliminará el archivo de forma permanente."
      />
    </div>
  );
}
