import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Usuario } from '../types';

interface UsuarioTableProps {
  usuarios: Usuario[];
  isLoading: boolean;
  onEdit: (usuario: Usuario) => void;
}

const ROL_LABELS: Record<string, string> = {
  ALUMNO: 'Alumno',
  TUTOR: 'Tutor',
  PROFESOR: 'Profesor',
  COORDINADOR: 'Coordinador',
  NEXO: 'Nexo',
  ADMIN: 'Admin',
  FINANZAS: 'Finanzas',
};

function formatearFecha(iso: string): string {
  return new Date(iso).toLocaleDateString('es-AR');
}

export function UsuarioTable({ usuarios, isLoading, onEdit }: UsuarioTableProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!usuarios || usuarios.length === 0) {
    return <EmptyState message="No se encontraron usuarios" icon="person" />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left text-label-md">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="px-4 py-3 font-medium text-on-surface">Nombre</th>
            <th className="px-4 py-3 font-medium text-on-surface">Email</th>
            <th className="px-4 py-3 font-medium text-on-surface">Rol</th>
            <th className="px-4 py-3 font-medium text-on-surface">Estado</th>
            <th className="px-4 py-3 font-medium text-on-surface">Creado</th>
            <th className="px-4 py-3 font-medium text-on-surface">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((usuario) => (
            <tr
              key={usuario.id}
              className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
            >
              <td className="px-4 py-3 text-on-surface font-medium">
                {usuario.nombre} {usuario.apellido}
              </td>
              <td className="px-4 py-3 text-on-surface-variant">
                {usuario.email}
              </td>
              <td className="px-4 py-3">
                <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-label-xs font-medium text-primary">
                  {ROL_LABELS[usuario.rol] ?? usuario.rol}
                </span>
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${
                    usuario.activo
                      ? 'bg-success/10 text-success'
                      : 'bg-error/10 text-error'
                  }`}
                >
                  {usuario.activo ? 'Activo' : 'Inactivo'}
                </span>
              </td>
              <td className="px-4 py-3 text-on-surface-variant">
                {formatearFecha(usuario.created_at)}
              </td>
              <td className="px-4 py-3">
                <button
                  type="button"
                  onClick={() => onEdit(usuario)}
                  className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                  title="Editar"
                >
                  <span className="material-symbols-outlined text-[18px]">edit</span>
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
