import { useState, useCallback } from 'react';
import { useUsuarios, useCrearUsuario, useEditarUsuario } from '../hooks/useUsuarios';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { UsuarioFilters, type UsuarioFilterValues } from '../components/UsuarioFilters';
import { UsuarioTable } from '../components/UsuarioTable';
import { UsuarioFormModal } from '../components/UsuarioFormModal';
import { Button } from '@/shared/components/ds';
import type { Usuario, CrearUsuarioData, EditarUsuarioData } from '../types';

const initialFilters: UsuarioFilterValues = {
  rol: '',
  activo: '',
  q: '',
};

export function UsuariosPage() {
  const { hasPermission } = useAuth();
  const [filters, setFilters] = useState<UsuarioFilterValues>(initialFilters);
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const [showFormModal, setShowFormModal] = useState(false);
  const [editingUsuario, setEditingUsuario] = useState<Usuario | null>(null);

  const canCreate = hasPermission('admin:usuarios:crear');
  const canEdit = hasPermission('admin:usuarios:editar');

  const appliedFilters: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(filters)) {
    if (value !== '' && value !== undefined) {
      if (key === 'activo') {
        appliedFilters[key] = value === 'true';
      } else {
        appliedFilters[key] = value;
      }
    }
  }

  const { data, isLoading, isError } = useUsuarios({
    ...appliedFilters,
    offset: page * pageSize,
    limit: pageSize,
  });

  const crearUsuario = useCrearUsuario();
  const editarUsuario = useEditarUsuario();

  const handleFilterChange = (key: string, value: unknown) => {
    setPage(0);
    setFilters((prev) => ({ ...prev, [key]: value as string }));
  };

  const handleClearFilters = () => {
    setPage(0);
    setFilters(initialFilters);
  };

  const handleOpenCreate = () => {
    setEditingUsuario(null);
    setShowFormModal(true);
  };

  const handleOpenEdit = (usuario: Usuario) => {
    setEditingUsuario(usuario);
    setShowFormModal(true);
  };

  const handleCloseFormModal = () => {
    setShowFormModal(false);
    setEditingUsuario(null);
  };

  const handleSave = useCallback(
    async (formData: CrearUsuarioData | EditarUsuarioData) => {
      if (editingUsuario) {
        await editarUsuario.mutateAsync({ id: editingUsuario.id, data: formData });
      } else {
        await crearUsuario.mutateAsync(formData as CrearUsuarioData);
      }
    },
    [editingUsuario, editarUsuario, crearUsuario],
  );

  const usuarios = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Usuarios</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Gestioná los usuarios del sistema
          </p>
        </div>
        {canCreate && (
          <Button type="button" variant="primary" icon="add" onClick={handleOpenCreate}>
            Nuevo usuario
          </Button>
        )}
      </div>

      <UsuarioFilters
        values={filters}
        onChange={handleFilterChange}
        onClear={handleClearFilters}
      />

      {isError ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <span className="material-symbols-outlined text-[48px] text-error mb-3">error</span>
          <p className="text-body-md text-on-surface-variant">Error al cargar los usuarios</p>
        </div>
      ) : (
        <>
          <UsuarioTable
            usuarios={usuarios}
            isLoading={isLoading}
            onEdit={canEdit ? handleOpenEdit : () => {}}
          />

          {total > pageSize && (
            <div className="flex items-center justify-center gap-2">
              <Button variant="secondary" size="sm" icon="chevron_left" onClick={() => setPage((p) => Math.max(0, p - 1))} disabled={page === 0}>
                Anterior
              </Button>
              <span style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>Página {page + 1} de {totalPages}</span>
              <Button variant="secondary" size="sm" trailingIcon="chevron_right" onClick={() => setPage((p) => p + 1)} disabled={(page + 1) * pageSize >= total}>
                Siguiente
              </Button>
            </div>
          )}
        </>
      )}

      <UsuarioFormModal
        isOpen={showFormModal}
        onClose={handleCloseFormModal}
        onSave={handleSave}
        selectedItem={editingUsuario}
      />
    </div>
  );
}
