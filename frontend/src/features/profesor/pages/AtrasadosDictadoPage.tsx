import { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  useAtrasadosProfesor,
  useActividadesDictado,
} from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import { ComunicadoFlexibleForm } from '@/features/academico/components/ComunicadoFlexibleForm';
import type { AtrasadoProfesor, ComunicadoDestinatario } from '../types';

// ---------- Types ----------

interface IndividualComunicadoState {
  titulo: string;
  destinatarios: ComunicadoDestinatario[];
}

// ---------- AtrasadoGroup sub-component ----------

function AtrasadoGroup({
  titulo,
  alumnos,
  dictadoId,
  icon,
  iconColor,
  onGenerarComunicado,
  onIndividualComunicado,
}: {
  titulo: string;
  alumnos: AtrasadoProfesor[];
  dictadoId: string;
  icon: string;
  iconColor: string;
  onGenerarComunicado: () => void;
  onIndividualComunicado: (state: IndividualComunicadoState) => void;
}) {
  if (alumnos.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[20px]" style={{ color: iconColor }}>{icon}</span>
          <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>{titulo}</h4>
        </div>
        <Button variant="primary" size="sm" onClick={onGenerarComunicado}>
          <span className="material-symbols-outlined text-[16px]">send</span>
          Generar comunicado
        </Button>
      </div>
      <div className="overflow-x-auto rounded-xl border border-outline-variant">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container-low">
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Nombre</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Apellido</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Desaprobadas</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Sin entregar</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant"></th>
            </tr>
          </thead>
          <tbody>
            {alumnos.map((a) => (
              <tr key={a.alumno_id} className="border-b border-outline-variant hover:bg-surface-container-low">
                <td className="px-4 py-2 text-body-sm text-on-surface">{a.nombre}</td>
                <td className="px-4 py-2 text-body-sm text-on-surface">{a.apellido}</td>
                <td className="px-4 py-2 text-body-sm text-on-surface-variant">{a.actividades_desaprobadas}</td>
                <td className="px-4 py-2 text-body-sm text-on-surface-variant">{a.actividades_atrasado_null}</td>
                <td className="px-4 py-2 text-right">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() =>
                      onIndividualComunicado({
                        titulo: `Comunicado para ${a.apellido}, ${a.nombre}`,
                        // alumno_id in AtrasadoProfesor IS the entrada_padron_id (backend sets entrada.id)
                        destinatarios: [{ entrada_padron_id: a.alumno_id, dictado_id: dictadoId }],
                      })
                    }
                  >
                    <span className="material-symbols-outlined text-[14px]">send</span>
                    Comunicado individual
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ---------- Main Page ----------

export function AtrasadosDictadoPage() {
  const { dictadoId } = useParams<{ dictadoId: string }>();
  const [comunicado, setComunicado] = useState<IndividualComunicadoState | null>(null);

  const { data, isLoading, isError } = useAtrasadosProfesor(dictadoId!);
  // Keep actividades query warm for sibling tabs (no local usage needed)
  useActividadesDictado(dictadoId!);

  const desaprobados = (data ?? []).filter(
    (a: AtrasadoProfesor) => a.estado === 'atrasado' && a.subtipo === 'desaprobado',
  );
  const atrasadoNull = (data ?? []).filter(
    (a: AtrasadoProfesor) => a.estado === 'atrasado' && a.subtipo === 'atrasado_null',
  );
  const totalAtrasados = desaprobados.length + atrasadoNull.length;

  const buildGeneralState = (alumnos: AtrasadoProfesor[], titulo: string): IndividualComunicadoState => ({
    titulo,
    destinatarios: alumnos.map((a) => ({ entrada_padron_id: a.alumno_id, dictado_id: dictadoId! })),
  });

  if (isLoading) return <LoadingState rows={5} cols={4} />;
  if (isError) return <EmptyState message="Error al cargar los atrasados" icon="error" />;

  return (
    <div className="space-y-6">
      <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>
        Alumnos Atrasados ({totalAtrasados})
      </h3>

      {comunicado && (
        <ComunicadoFlexibleForm
          titulo={comunicado.titulo}
          destinatarios={comunicado.destinatarios}
          onClose={() => setComunicado(null)}
        />
      )}

      {!comunicado && (
        <>
          <AtrasadoGroup
            titulo={`Desaprobados (${desaprobados.length})`}
            alumnos={desaprobados}
            dictadoId={dictadoId!}
            icon="cancel"
            iconColor="var(--error)"
            onGenerarComunicado={() =>
              setComunicado(buildGeneralState(desaprobados, 'Comunicado a desaprobados'))
            }
            onIndividualComunicado={setComunicado}
          />

          <AtrasadoGroup
            titulo={`Sin entregar (${atrasadoNull.length})`}
            alumnos={atrasadoNull}
            dictadoId={dictadoId!}
            icon="schedule"
            iconColor="var(--warning, #f59e0b)"
            onGenerarComunicado={() =>
              setComunicado(buildGeneralState(atrasadoNull, 'Comunicado a sin entregar'))
            }
            onIndividualComunicado={setComunicado}
          />

          {totalAtrasados === 0 && (
            <EmptyState message="Todos los alumnos están al día" icon="check_circle" />
          )}
        </>
      )}
    </div>
  );
}
