import { useState } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { LiquidacionDocente, LiquidacionPeriodo } from '../types/liquidaciones';

interface LiquidacionTableProps {
  liquidacion: LiquidacionPeriodo | undefined;
  isLoading: boolean;
}

function DocenteDetailRow({ docente }: { docente: LiquidacionDocente }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <tr
        className="cursor-pointer border-b border-outline-variant transition-colors hover:bg-surface-container-low"
        onClick={() => setExpanded(!expanded)}
      >
        <td className="px-4 py-3">
          <span className="material-symbols-outlined text-[18px] text-outline transition-transform" style={{ transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)' }}>
            chevron_right
          </span>
        </td>
        <td className="px-4 py-3 text-body-sm text-on-surface font-medium">
          {docente.docente_apellido}, {docente.docente_nombre}
        </td>
        <td className="px-4 py-3 text-body-sm text-on-surface-variant">
          <span className="inline-flex rounded-full bg-primary/10 px-2.5 py-0.5 text-label-xs font-medium text-primary">
            {docente.rol}
          </span>
        </td>
        <td className="px-4 py-3 text-body-sm text-on-surface text-right">
          ${docente.comisiones.toLocaleString('es-AR')}
        </td>
        <td className="px-4 py-3 text-body-sm text-on-surface text-right">
          ${docente.salario_base.toLocaleString('es-AR')}
        </td>
        <td className="px-4 py-3 text-body-sm text-on-surface text-right">
          ${docente.plus.toLocaleString('es-AR')}
        </td>
        <td className="px-4 py-3 text-body-sm text-on-surface font-semibold text-right">
          ${docente.total.toLocaleString('es-AR')}
        </td>
      </tr>
      {expanded && (
        <tr className="bg-surface-container-low">
          <td colSpan={7} className="px-4 py-3">
            <div className="rounded-lg border border-outline-variant bg-surface p-4">
              <h4 className="text-label-sm text-on-surface-variant mb-2">Detalle de liquidación</h4>
              <div className="grid grid-cols-2 gap-4 text-body-sm">
                <div>
                  <span className="text-on-surface-variant">Salario base: </span>
                  <span className="text-on-surface font-medium">${docente.salario_base.toLocaleString('es-AR')}</span>
                </div>
                <div>
                  <span className="text-on-surface-variant">Comisiones: </span>
                  <span className="text-on-surface font-medium">${docente.comisiones.toLocaleString('es-AR')}</span>
                </div>
                <div>
                  <span className="text-on-surface-variant">Plus: </span>
                  <span className="text-on-surface font-medium">${docente.plus.toLocaleString('es-AR')}</span>
                </div>
                <div>
                  <span className="text-on-surface-variant">Total: </span>
                  <span className="text-on-surface font-semibold">${docente.total.toLocaleString('es-AR')}</span>
                </div>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export function LiquidacionTable({ liquidacion, isLoading }: LiquidacionTableProps) {
  if (isLoading) {
    return <LoadingState rows={5} cols={6} />;
  }

  if (!liquidacion) {
    return <EmptyState message="Seleccioná un período para ver la liquidación" icon="payments" />;
  }

  const docentes = liquidacion.docentes;

  if (docentes.length === 0) {
    return <EmptyState message="No hay docentes en esta liquidación" icon="people" />;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            <th className="w-10 px-4 py-3" />
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Docente</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Rol</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant text-right">Comisiones</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant text-right">Salario base</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant text-right">Plus</th>
            <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant text-right">Total</th>
          </tr>
        </thead>
        <tbody>
          {docentes.map((docente) => (
            <DocenteDetailRow key={docente.id} docente={docente} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
