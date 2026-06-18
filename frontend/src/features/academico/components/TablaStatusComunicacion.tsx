import type { MensajeStatusEntry } from '../types';
import { StatusBadge } from './StatusBadge';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';

interface TablaStatusComunicacionProps {
  mensajes?: MensajeStatusEntry[];
  isLoading?: boolean;
  isTerminal?: boolean;
}

export function TablaStatusComunicacion({ mensajes, isLoading, isTerminal }: TablaStatusComunicacionProps) {
  if (isLoading) {
    return <LoadingState rows={4} cols={4} />;
  }

  if (!mensajes || mensajes.length === 0) {
    return <EmptyState message="No hay comunicaciones enviadas" />;
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <p className="text-label-sm font-medium text-on-surface">
          Estado de envíos ({mensajes.length})
        </p>
        {isTerminal && (
          <span className="text-label-xs text-success">Todos los envíos finalizados</span>
        )}
        {!isTerminal && (
          <div className="flex items-center gap-1">
            <span className="h-2 w-2 animate-pulse rounded-full bg-info" />
            <span className="text-label-xs text-info">Actualizando...</span>
          </div>
        )}
      </div>
      <div className="overflow-x-auto rounded-xl border border-outline-variant">
        <table className="w-full text-left text-label-md">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container-low">
              <th className="px-4 py-3 font-medium text-on-surface">Nombre</th>
              <th className="px-4 py-3 font-medium text-on-surface">Email</th>
              <th className="px-4 py-3 font-medium text-on-surface">Estado</th>
              <th className="px-4 py-3 font-medium text-on-surface">Actualización</th>
            </tr>
          </thead>
          <tbody>
            {mensajes.map((msg) => (
              <tr
                key={msg.alumno.id}
                className={`border-b border-outline-variant transition-colors hover:bg-surface-container-low ${
                  msg.status === 'Fallido' ? 'bg-error/5' : ''
                }`}
                title={msg.error ?? undefined}
              >
                <td className="px-4 py-3 text-on-surface font-medium">
                  {msg.alumno.apellido}, {msg.alumno.nombre}
                </td>
                <td className="px-4 py-3 text-on-surface-variant">{msg.alumno.email}</td>
                <td className="px-4 py-3">
                  <StatusBadge status={msg.status} />
                </td>
                <td className="px-4 py-3 text-on-surface-variant text-label-xs">
                  {new Date(msg.updated_at).toLocaleTimeString('es-AR')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
