import type { InstanciaEncuentro, InstanciaEstado } from '../types';

interface EncuentroInstanceRowProps {
  instance: InstanciaEncuentro;
  onEstadoChange?: (id: string, estado: InstanciaEstado) => void;
}

const estadoConfig: Record<InstanciaEstado, { label: string; className: string }> = {
  Pendiente: { label: 'Pendiente', className: 'bg-warning/10 text-warning' },
  Realizado: { label: 'Realizado', className: 'bg-success/10 text-success' },
  Cancelado: { label: 'Cancelado', className: 'bg-error/10 text-error' },
};

export function EncuentroInstanceRow({ instance, onEstadoChange }: EncuentroInstanceRowProps) {
  const estado = estadoConfig[instance.estado];

  return (
    <div className="flex items-center gap-4 rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="font-medium text-on-surface">{instance.titulo}</span>
          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${estado.className}`}>
            {estado.label}
          </span>
        </div>
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-label-sm text-on-surface-variant">
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">calendar_today</span>
            {instance.fecha}
          </span>
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">schedule</span>
            {instance.hora_inicio} - {instance.hora_fin}
          </span>
          {instance.materia_nombre && (
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">book</span>
              {instance.materia_nombre}
            </span>
          )}
          {instance.docente_nombre && (
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">person</span>
              {instance.docente_nombre}
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        {instance.url_meet && (
          <a
            href={instance.url_meet}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 rounded-lg bg-primary/10 px-3 py-1.5 text-label-sm font-medium text-primary transition-colors hover:bg-primary/20"
          >
            <span className="material-symbols-outlined text-[16px]">videocam</span>
            Meet
          </a>
        )}

        {onEstadoChange && (
          <select
            value={instance.estado}
            onChange={(e) => onEstadoChange(instance.id, e.target.value as InstanciaEstado)}
            className="rounded-lg border border-outline-variant bg-surface-container px-2 py-1.5 text-label-sm text-on-surface outline-none focus:border-primary"
          >
            <option value="Pendiente">Pendiente</option>
            <option value="Realizado">Realizado</option>
            <option value="Cancelado">Cancelado</option>
          </select>
        )}
      </div>
    </div>
  );
}
