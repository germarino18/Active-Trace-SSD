import { Link } from 'react-router-dom';
import type { AlumnoDashboardResponse } from '../types/alumno.types';

interface AlertasPanelProps {
  dashboard: AlumnoDashboardResponse;
}

export function AlertasPanel({ dashboard }: AlertasPanelProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-label-md font-medium text-on-surface">Alertas y próximos eventos</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {dashboard.avisos_no_leidos > 0 && (
          <Link
            to="/alumno/avisos"
            className="flex items-center gap-3 rounded-xl bg-primary/10 border border-primary/20 p-3 transition-colors hover:bg-primary/15"
          >
            <span className="material-symbols-outlined text-primary text-[24px]">campaign</span>
            <div>
              <p className="text-label-sm font-medium text-primary">{dashboard.avisos_no_leidos} aviso{dashboard.avisos_no_leidos !== 1 ? 's' : ''} no leído{dashboard.avisos_no_leidos !== 1 ? 's' : ''}</p>
              <p className="text-label-xs text-primary/70">Tenés avisos pendientes de lectura</p>
            </div>
          </Link>
        )}

        {dashboard.comunicaciones_no_leidas > 0 && (
          <Link
            to="/alumno/comunicaciones"
            className="flex items-center gap-3 rounded-xl bg-tertiary/10 border border-tertiary/20 p-3 transition-colors hover:bg-tertiary/15"
          >
            <span className="material-symbols-outlined text-tertiary text-[24px]">forward_to_inbox</span>
            <div>
              <p className="text-label-sm font-medium text-tertiary">{dashboard.comunicaciones_no_leidas} comunicacione{dashboard.comunicaciones_no_leidas !== 1 ? 's' : ''} no leída{dashboard.comunicaciones_no_leidas !== 1 ? 's' : ''}</p>
              <p className="text-label-xs text-tertiary/70">Revisá tus comunicaciones recibidas</p>
            </div>
          </Link>
        )}
      </div>

      {dashboard.proximos_coloquios.length > 0 && (
        <div className="rounded-xl bg-surface-container-lowest border border-outline-variant p-3">
          <h4 className="text-label-sm font-medium text-on-surface mb-2">Próximos coloquios</h4>
          <ul className="space-y-2">
            {dashboard.proximos_coloquios.map((c) => (
              <li key={c.id} className="flex items-center justify-between text-label-sm">
                <span className="text-on-surface truncate">{c.materia_nombre}</span>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-on-surface-variant">{new Date(c.fecha).toLocaleDateString('es-AR')}</span>
                  <span className="text-label-xs text-tertiary">{c.cupos_restantes} cupo{c.cupos_restantes !== 1 ? 's' : ''}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {dashboard.proximas_fechas.length > 0 && (
        <div className="rounded-xl bg-surface-container-lowest border border-outline-variant p-3">
          <h4 className="text-label-sm font-medium text-on-surface mb-2">Próximas fechas académicas</h4>
          <ul className="space-y-2">
            {dashboard.proximas_fechas.map((f) => (
              <li key={f.id} className="flex items-start gap-2 text-label-sm">
                <span className="material-symbols-outlined text-[16px] text-outline mt-0.5">calendar_month</span>
                <div className="flex-1 min-w-0">
                  <p className="text-on-surface truncate">{f.descripcion}</p>
                  <p className="text-label-xs text-on-surface-variant">
                    {f.materia_nombre} &middot; {new Date(f.fecha).toLocaleDateString('es-AR')}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
