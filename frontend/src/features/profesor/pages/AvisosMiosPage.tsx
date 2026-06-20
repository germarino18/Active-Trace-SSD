import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAvisosMios, useMutationCrearAviso, useProfesorDashboard } from '../hooks/useProfesor';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import type { AvisoCreate, AvisoProfesor } from '../types';

const severityStyles: Record<string, string> = {
  INFO: 'bg-blue-500/10 text-blue-600',
  ADVERTENCIA: 'bg-yellow-500/10 text-yellow-700',
  CRITICO: 'bg-red-500/10 text-red-600',
};

const severityLabels: Record<string, string> = {
  INFO: 'Info',
  ADVERTENCIA: 'Advertencia',
  CRITICO: 'Crítico',
};

const avisoSchema = z.object({
  titulo: z.string().min(1, 'Requerido'),
  cuerpo: z.string().min(1, 'Requerido'),
  severidad: z.enum(['INFO', 'ADVERTENCIA', 'CRITICO']),
  alcance: z.enum(['POR_MATERIA', 'POR_COHORTE']),
  materia_id: z.string().optional(),
  cohorte_id: z.string().optional(),
  inicio_en: z.string().min(1, 'Requerido'),
  fin_en: z.string().min(1, 'Requerido'),
  requiere_ack: z.boolean(),
  orden: z.coerce.number().min(0),
});

type AvisoForm = z.infer<typeof avisoSchema>;

function CrearAvisoForm({ onClose }: { onClose: () => void }) {
  const mutation = useMutationCrearAviso();
  const { data: dashboard } = useProfesorDashboard();
  const dictados = dashboard?.materias_asignadas ?? [];

  const { register, handleSubmit, watch, formState: { errors } } = useForm<AvisoForm>({
    resolver: zodResolver(avisoSchema),
    defaultValues: {
      titulo: '', cuerpo: '', severidad: 'INFO', alcance: 'POR_MATERIA',
      inicio_en: '', fin_en: '', requiere_ack: false, orden: 0,
    },
  });

  const alcance = watch('alcance');

  const onSubmit = async (values: AvisoForm) => {
    const payload: AvisoCreate = {
      alcance: values.alcance,
      materia_id: values.alcance === 'POR_MATERIA' ? values.materia_id || null : null,
      cohorte_id: values.alcance === 'POR_COHORTE' ? values.cohorte_id || null : null,
      severidad: values.severidad,
      titulo: values.titulo,
      cuerpo: values.cuerpo,
      inicio_en: new Date(values.inicio_en).toISOString(),
      fin_en: new Date(values.fin_en).toISOString(),
      requiere_ack: values.requiere_ack,
      orden: values.orden,
    };
    try {
      await mutation.mutateAsync(payload);
      onClose();
    } catch {
      // handled via mutation.isError
    }
  };

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-4">
      <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>Crear aviso</h4>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
        <div>
          <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Título *</label>
          <input {...register('titulo')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary" />
          {errors.titulo && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.titulo.message}</p>}
        </div>

        <div>
          <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Mensaje *</label>
          <textarea {...register('cuerpo')} rows={3} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary resize-none" />
          {errors.cuerpo && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.cuerpo.message}</p>}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Alcance *</label>
            <select {...register('alcance')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary">
              <option value="POR_MATERIA">Por materia</option>
              <option value="POR_COHORTE">Por cohorte</option>
            </select>
          </div>
          <div>
            {alcance === 'POR_MATERIA' ? (
              <>
                <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Materia</label>
                <select {...register('materia_id')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary">
                  <option value="">— Seleccionar materia —</option>
                  {dictados.map((d) => (
                    <option key={d.dictado_id} value={d.materia_id}>{d.materia_nombre}</option>
                  ))}
                </select>
              </>
            ) : (
              <>
                <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Cohorte ID</label>
                <input {...register('cohorte_id')} placeholder="UUID de la cohorte" className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary" />
              </>
            )}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div>
            <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Severidad</label>
            <select {...register('severidad')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary">
              <option value="INFO">Info</option>
              <option value="ADVERTENCIA">Advertencia</option>
              <option value="CRITICO">Crítico</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Vigente desde *</label>
            <input type="date" {...register('inicio_en')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary" />
            {errors.inicio_en && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.inicio_en.message}</p>}
          </div>
          <div>
            <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Vigente hasta *</label>
            <input type="date" {...register('fin_en')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary" />
            {errors.fin_en && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.fin_en.message}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input type="checkbox" {...register('requiere_ack')} id="ack_check" className="h-4 w-4" />
          <label htmlFor="ack_check" style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>Requiere confirmación de lectura</label>
        </div>

        <div style={{ display: 'flex', gap: 8 }}>
          <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
            {mutation.isPending ? 'Creando…' : 'Crear aviso'}
          </Button>
          <Button type="button" variant="secondary" size="sm" onClick={onClose}>Cancelar</Button>
        </div>

        {mutation.isError && (
          <p style={{ fontSize: 13, color: 'var(--error)' }}>
            Error al crear el aviso. Verificá el alcance y los campos requeridos.
          </p>
        )}
      </form>
    </div>
  );
}

export function AvisosMiosPage() {
  const [showCrear, setShowCrear] = useState(false);
  // Backend returns a plain array — not {items, total}
  const { data: avisos, isLoading, isError } = useAvisosMios();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>Mis Avisos</h3>
        <Button variant="primary" size="sm" onClick={() => setShowCrear((v) => !v)}>
          <span className="material-symbols-outlined text-[16px]">add</span>
          Crear aviso
        </Button>
      </div>

      {showCrear && <CrearAvisoForm onClose={() => setShowCrear(false)} />}

      {isLoading ? (
        <LoadingState rows={4} cols={4} />
      ) : isError ? (
        <EmptyState message="Error al cargar los avisos" icon="error" />
      ) : !avisos || avisos.length === 0 ? (
        <EmptyState message="No tenés avisos disponibles" icon="campaign" />
      ) : (
        <div className="space-y-3">
          {avisos.map((aviso: AvisoProfesor) => (
            <div
              key={aviso.id}
              className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-1"
            >
              <div className="flex items-start justify-between gap-3">
                <span style={{ fontWeight: 600, fontSize: 15, color: 'var(--on-surface)' }}>{aviso.titulo}</span>
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${severityStyles[aviso.severidad] ?? 'bg-outline/10 text-on-surface-variant'}`}
                >
                  {severityLabels[aviso.severidad] ?? aviso.severidad}
                </span>
              </div>
              <p style={{ margin: 0, fontSize: 14, color: 'var(--on-surface-variant)' }}>{aviso.cuerpo}</p>
              <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--outline)' }}>
                <span>Vigente hasta: {new Date(aviso.fin_en).toLocaleDateString()}</span>
                {aviso.acknowledged && (
                  <span style={{ color: 'var(--success)' }}>✓ Leído</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
