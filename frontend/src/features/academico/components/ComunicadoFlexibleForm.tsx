/**
 * ComunicadoFlexibleForm — dialog to send a flexible comunicado (individual or
 * general) to a pre-built `destinatarios` set. `actividad_id` is OPTIONAL:
 * submitting without an activity sends `actividad_id: null` ("obviar actividad").
 * Reuses the approval-gated pipeline via useMutationComunicadoFlexible.
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutationComunicadoFlexible } from '@/features/profesor/hooks/useProfesor';
import { Button } from '@/shared/components/ds';
import type { ComunicadoDestinatario, ComunicadoResult } from '@/features/profesor/types';

const schema = z.object({
  actividad_id: z.string().optional(),
  asunto_template: z.string().min(1, 'Requerido'),
  cuerpo_template: z.string().min(1, 'Requerido'),
});
type FormValues = z.infer<typeof schema>;

const inputCls =
  'w-full mt-1 rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary';

export function ComunicadoFlexibleForm({
  titulo,
  destinatarios,
  materias,
  onClose,
}: {
  titulo: string;
  destinatarios: ComunicadoDestinatario[];
  materias?: string;
  onClose: () => void;
}) {
  const mutation = useMutationComunicadoFlexible();
  const [result, setResult] = useState<ComunicadoResult | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { actividad_id: '', asunto_template: '', cuerpo_template: '' },
  });

  const onSubmit = async (values: FormValues) => {
    const res = await mutation.mutateAsync({
      actividad_id: values.actividad_id ? values.actividad_id : null,
      asunto_template: values.asunto_template,
      cuerpo_template: values.cuerpo_template,
      destinatarios,
    });
    setResult(res);
  };

  return (
    <div
      role="dialog"
      aria-label={titulo}
      className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3"
    >
      <h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: 'var(--on-surface)' }}>{titulo}</h3>
      <p style={{ margin: 0, fontSize: 13, color: 'var(--on-surface-variant)' }}>
        {destinatarios.length} destinatario{destinatarios.length !== 1 ? 's' : ''}
        {materias ? ` · ${materias}` : ''}
      </p>

      {result ? (
        <div className="space-y-2">
          <p style={{ margin: 0, fontSize: 14, color: 'var(--tertiary)', fontWeight: 600 }}>
            Comunicado enviado a {result.total} alumno{result.total !== 1 ? 's' : ''}.
            {result.lote_id ? ` Lote: ${result.lote_id}` : ''}
          </p>
          <Button variant="secondary" size="sm" onClick={onClose}>Cerrar</Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
          <div>
            <label htmlFor="comunicado-asunto" style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>
              Asunto
            </label>
            <input id="comunicado-asunto" className={inputCls} {...register('asunto_template')} />
            {errors.asunto_template && (
              <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.asunto_template.message}</p>
            )}
          </div>
          <div>
            <label htmlFor="comunicado-cuerpo" style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>
              Cuerpo del mensaje
            </label>
            <textarea
              id="comunicado-cuerpo"
              rows={4}
              className={`${inputCls} resize-none`}
              {...register('cuerpo_template')}
            />
            {errors.cuerpo_template && (
              <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.cuerpo_template.message}</p>
            )}
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
              {mutation.isPending ? 'Enviando…' : 'Enviar comunicado'}
            </Button>
            <Button type="button" variant="secondary" size="sm" onClick={onClose}>Cancelar</Button>
          </div>
          {mutation.isError && (
            <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al enviar el comunicado</p>
          )}
        </form>
      )}
    </div>
  );
}
