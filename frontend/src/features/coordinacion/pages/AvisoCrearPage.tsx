import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCrearAviso } from '../hooks/useAvisos';
import { ScopeSelector } from '../components/ScopeSelector';
import type { AvisoScope } from '../types';
import { Button } from '@/shared/components/ds';

const avisoSchema = z.object({
  titulo: z.string().min(1, 'El título es requerido'),
  cuerpo: z.string().min(1, 'El mensaje es requerido'),
  severidad: z.enum(['INFO', 'ADVERTENCIA', 'CRITICO']),
  inicio_en: z.string().min(1, 'La fecha de inicio es requerida'),
  fin_en: z.string().min(1, 'La fecha de fin es requerida'),
  requiere_ack: z.boolean(),
  orden: z.number().min(0, 'Debe ser un número positivo'),
});

type AvisoForm = z.infer<typeof avisoSchema>;

export function AvisoCrearPage() {
  const navigate = useNavigate();
  const crearAviso = useCrearAviso();
  const [scopeType, setScopeType] = useState<AvisoScope>('GLOBAL');
  const [scopeValue, setScopeValue] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AvisoForm>({
    resolver: zodResolver(avisoSchema),
    defaultValues: {
      titulo: '',
      cuerpo: '',
      severidad: 'INFO',
      inicio_en: '',
      fin_en: '',
      requiere_ack: false,
      orden: 0,
    },
  });

  const onSubmit = async (data: AvisoForm) => {
    try {
      const scopeFields: Record<string, string | undefined> = {};
      if (scopeType === 'POR_MATERIA') scopeFields.materia_id = scopeValue || undefined;
      else if (scopeType === 'POR_COHORTE') scopeFields.cohorte_id = scopeValue || undefined;
      else if (scopeType === 'POR_ROL') scopeFields.rol_destino = scopeValue || undefined;

      await crearAviso.mutateAsync({
        ...data,
        ...scopeFields,
        alcance: scopeType,
      });
      navigate('/avisos');
    } catch {
      // handled by mutation error state
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Crear Aviso</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Creá un nuevo aviso o comunicación para el sistema.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
          <input
            {...register('titulo')}
            placeholder="Ej: Recordatorio de carga de actas"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.titulo && <p className="mt-1 text-label-xs text-error">{errors.titulo.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Mensaje</label>
          <textarea
            {...register('cuerpo')}
            rows={4}
            placeholder="Contenido del aviso..."
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.cuerpo && <p className="mt-1 text-label-xs text-error">{errors.cuerpo.message}</p>}
        </div>

        <ScopeSelector
          scopeType={scopeType}
          scopeValue={scopeValue}
          onScopeTypeChange={setScopeType}
          onScopeValueChange={setScopeValue}
        />

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Severidad</label>
          <select
            {...register('severidad')}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
          >
            <option value="INFO">Info</option>
            <option value="ADVERTENCIA">Advertencia</option>
            <option value="CRITICO">Crítico</option>
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Vigencia desde</label>
            <input
              type="date"
              {...register('inicio_en')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
            />
            {errors.inicio_en && <p className="mt-1 text-label-xs text-error">{errors.inicio_en.message}</p>}
          </div>
          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Vigencia hasta</label>
            <input
              type="date"
              {...register('fin_en')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
            />
            {errors.fin_en && <p className="mt-1 text-label-xs text-error">{errors.fin_en.message}</p>}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            {...register('requiere_ack')}
            id="requiere_ack"
            className="h-4 w-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary"
          />
          <label htmlFor="requiere_ack" className="text-label-sm text-on-surface-variant">
            Requiere confirmación de lectura
          </label>
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Orden</label>
          <input
            type="number"
            {...register('orden', { valueAsNumber: true })}
            min={0}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
          />
          {errors.orden && <p className="mt-1 text-label-xs text-error">{errors.orden.message}</p>}
        </div>

        <div className="flex gap-3">
          <Button
            type="submit"
            variant="primary"
            disabled={crearAviso.isPending}
          >
            Crear Aviso
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate('/avisos')}
          >
            Cancelar
          </Button>
        </div>

        {crearAviso.isError && (
          <div className="rounded-xl border border-error/30 bg-error/5 p-4 text-body-sm text-error">
            Error al crear el aviso. Intentá de nuevo.
          </div>
        )}
      </form>
    </div>
  );
}
