import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  useAtrasadosProfesor,
  useActividadesDictado,
  useMutationComunicadoAtrasados,
} from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import type { AtrasadoProfesor, ComunicadoAtrasadosData } from '../types';

const comunicadoSchema = z.object({
  actividad_id: z.string().min(1, 'Seleccioná una actividad'),
  asunto_template: z.string().min(1, 'Requerido'),
  cuerpo_template: z.string().min(1, 'Requerido'),
});

type ComunicadoForm = z.infer<typeof comunicadoSchema>;

export function AtrasadosDictadoPage() {
  const { dictadoId } = useParams<{ dictadoId: string }>();
  const [showComunicadoForm, setShowComunicadoForm] = useState(false);
  const [activeSubtipo, setActiveSubtipo] = useState<'desaprobado' | 'atrasado_null' | null>(null);
  const [comunicadoResult, setComunicadoResult] = useState<{ total: number; lote_id: string | null } | null>(null);

  const { data, isLoading, isError } = useAtrasadosProfesor(dictadoId!);
  const { data: actividades } = useActividadesDictado(dictadoId!);
  const comunicadoMutation = useMutationComunicadoAtrasados(dictadoId!);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<ComunicadoForm>({
    resolver: zodResolver(comunicadoSchema),
    defaultValues: { asunto_template: 'Actividad pendiente', cuerpo_template: 'Te recordamos que tenés una actividad pendiente.' },
  });

  // Only show alumnos with estado==='atrasado' (hide aprobados)
  const desaprobados = (data ?? []).filter((a: AtrasadoProfesor) => a.estado === 'atrasado' && a.subtipo === 'desaprobado');
  const atrasadoNull = (data ?? []).filter((a: AtrasadoProfesor) => a.estado === 'atrasado' && a.subtipo === 'atrasado_null');

  const openComunicado = (subtipo: 'desaprobado' | 'atrasado_null') => {
    setActiveSubtipo(subtipo);
    setShowComunicadoForm(true);
    reset({ asunto_template: 'Actividad pendiente', cuerpo_template: 'Te recordamos que tenés una actividad pendiente.' });
  };

  const onSubmit = async (values: ComunicadoForm) => {
    if (!activeSubtipo) return;
    const payload: ComunicadoAtrasadosData = {
      actividad_id: values.actividad_id,
      subtipo: activeSubtipo,
      asunto_template: values.asunto_template,
      cuerpo_template: values.cuerpo_template,
    };
    const result = await comunicadoMutation.mutateAsync(payload);
    setComunicadoResult(result);
    setShowComunicadoForm(false);
    setActiveSubtipo(null);
    reset();
  };

  if (isLoading) return <LoadingState rows={5} cols={4} />;
  if (isError) return <EmptyState message="Error al cargar los atrasados" icon="error" />;

  const totalAtrasados = desaprobados.length + atrasadoNull.length;

  return (
    <div className="space-y-6">
      <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>
        Alumnos Atrasados ({totalAtrasados})
      </h3>

      {comunicadoResult && (
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4">
          {comunicadoResult.total === 0 ? (
            <p style={{ margin: 0, color: 'var(--on-surface-variant)', fontSize: 14 }}>Sin destinatarios para el comunicado.</p>
          ) : (
            <p style={{ margin: 0, color: 'var(--tertiary)', fontSize: 14, fontWeight: 600 }}>
              Comunicado enviado a {comunicadoResult.total} alumnos. Lote: {comunicadoResult.lote_id}
            </p>
          )}
          <Button variant="ghost" size="sm" onClick={() => setComunicadoResult(null)}>Cerrar</Button>
        </div>
      )}

      {showComunicadoForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
          <h4 style={{ margin: 0, fontSize: 15, fontWeight: 600, color: 'var(--on-surface)' }}>
            Comunicado para alumnos {activeSubtipo === 'desaprobado' ? 'desaprobados' : 'sin entregar'}
          </h4>
          <div>
            <label style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>Actividad</label>
            <select {...register('actividad_id')} className="w-full mt-1 rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary">
              <option value="">Seleccioná una actividad</option>
              {(actividades ?? []).map((a) => (
                <option key={a.id} value={a.id}>{a.nombre}</option>
              ))}
            </select>
            {errors.actividad_id && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.actividad_id.message}</p>}
          </div>
          <div>
            <label style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>Asunto</label>
            <input {...register('asunto_template')} className="w-full mt-1 rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary" />
            {errors.asunto_template && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.asunto_template.message}</p>}
          </div>
          <div>
            <label style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>Cuerpo del mensaje</label>
            <textarea {...register('cuerpo_template')} rows={4} className="w-full mt-1 rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary resize-none" />
            {errors.cuerpo_template && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.cuerpo_template.message}</p>}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button type="submit" variant="primary" size="sm" disabled={comunicadoMutation.isPending}>
              {comunicadoMutation.isPending ? 'Enviando…' : 'Enviar comunicado'}
            </Button>
            <Button type="button" variant="secondary" size="sm" onClick={() => { setShowComunicadoForm(false); setActiveSubtipo(null); reset(); }}>
              Cancelar
            </Button>
          </div>
          {comunicadoMutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al enviar el comunicado</p>
          )}
        </form>
      )}

      <AtrasadoGroup
        titulo={`Desaprobados (${desaprobados.length})`}
        alumnos={desaprobados}
        icon="cancel"
        iconColor="var(--error)"
        subtipo="desaprobado"
        onComunicado={openComunicado}
        showingForm={showComunicadoForm && activeSubtipo === 'desaprobado'}
      />

      <AtrasadoGroup
        titulo={`Sin entregar (${atrasadoNull.length})`}
        alumnos={atrasadoNull}
        icon="schedule"
        iconColor="var(--warning, #f59e0b)"
        subtipo="atrasado_null"
        onComunicado={openComunicado}
        showingForm={showComunicadoForm && activeSubtipo === 'atrasado_null'}
      />

      {totalAtrasados === 0 && (
        <EmptyState message="Todos los alumnos están al día" icon="check_circle" />
      )}
    </div>
  );
}

function AtrasadoGroup({
  titulo,
  alumnos,
  icon,
  iconColor,
  subtipo,
  onComunicado,
  showingForm,
}: {
  titulo: string;
  alumnos: AtrasadoProfesor[];
  icon: string;
  iconColor: string;
  subtipo: 'desaprobado' | 'atrasado_null';
  onComunicado: (subtipo: 'desaprobado' | 'atrasado_null') => void;
  showingForm: boolean;
}) {
  if (alumnos.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[20px]" style={{ color: iconColor }}>{icon}</span>
          <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>{titulo}</h4>
        </div>
        {!showingForm && (
          <Button variant="primary" size="sm" onClick={() => onComunicado(subtipo)}>
            <span className="material-symbols-outlined text-[16px]">send</span>
            Generar comunicado
          </Button>
        )}
      </div>
      <div className="overflow-x-auto rounded-xl border border-outline-variant">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container-low">
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Nombre</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Apellido</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Desaprobadas</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Sin entregar</th>
            </tr>
          </thead>
          <tbody>
            {alumnos.map((a) => (
              <tr key={a.alumno_id} className="border-b border-outline-variant hover:bg-surface-container-low">
                <td className="px-4 py-2 text-body-sm text-on-surface">{a.nombre}</td>
                <td className="px-4 py-2 text-body-sm text-on-surface">{a.apellido}</td>
                <td className="px-4 py-2 text-body-sm text-on-surface-variant">{a.actividades_desaprobadas}</td>
                <td className="px-4 py-2 text-body-sm text-on-surface-variant">{a.actividades_atrasado_null}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
