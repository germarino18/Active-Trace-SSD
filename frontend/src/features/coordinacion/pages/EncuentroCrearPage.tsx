import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCrearSlotRecurrente, useCrearEncuentroUnico } from '../hooks/useEncuentros';
import { Button } from '@/shared/components/ds';

const recurrenteSchema = z.object({
  materia_id: z.string().min(1, 'Seleccioná una materia'),
  titulo: z.string().min(1, 'El título es requerido'),
  dia_semana: z.number().min(0).max(6),
  hora_inicio: z.string().min(1, 'La hora de inicio es requerida'),
  hora_fin: z.string().min(1, 'La hora de fin es requerida'),
  semanas: z.number().min(1, 'Al menos 1 semana').max(52, 'Máximo 52 semanas'),
  url_meet: z.string().url('URL inválida').optional().or(z.literal('')),
});

const unicoSchema = z.object({
  materia_id: z.string().min(1, 'Seleccioná una materia'),
  titulo: z.string().min(1, 'El título es requerido'),
  fecha: z.string().min(1, 'La fecha es requerida'),
  hora_inicio: z.string().min(1, 'La hora de inicio es requerida'),
  hora_fin: z.string().min(1, 'La hora de fin es requerida'),
  url_meet: z.string().url('URL inválida').optional().or(z.literal('')),
});

type RecurrenteForm = z.infer<typeof recurrenteSchema>;
type UnicoForm = z.infer<typeof unicoSchema>;

type Modo = 'recurrente' | 'unico';

const DIAS = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];

export function EncuentroCrearPage() {
  const navigate = useNavigate();
  const [modo, setModo] = useState<Modo>('unico');
  const [resultado, setResultado] = useState<string | null>(null);

  const crearSlot = useCrearSlotRecurrente();
  const crearUnico = useCrearEncuentroUnico();

  const recurrenteForm = useForm<RecurrenteForm>({
    resolver: zodResolver(recurrenteSchema),
    defaultValues: {
      materia_id: '',
      titulo: '',
      dia_semana: 1,
      hora_inicio: '18:00',
      hora_fin: '20:00',
      semanas: 8,
      url_meet: '',
    },
  });

  const unicoForm = useForm<UnicoForm>({
    resolver: zodResolver(unicoSchema),
    defaultValues: {
      materia_id: '',
      titulo: '',
      fecha: '',
      hora_inicio: '18:00',
      hora_fin: '20:00',
      url_meet: '',
    },
  });

  const onSubmitRecurrente = async (data: RecurrenteForm) => {
    try {
      const result = await crearSlot.mutateAsync({
        ...data,
        url_meet: data.url_meet || undefined,
      });
      setResultado(`¡${result.instancias} instancias generadas correctamente!`);
    } catch {
      setResultado('Error al crear el slot recurrente');
    }
  };

  const onSubmitUnico = async (data: UnicoForm) => {
    try {
      const instancia = await crearUnico.mutateAsync({
        ...data,
        url_meet: data.url_meet || undefined,
      });
      navigate(`/encuentros/${instancia.id}`);
    } catch {
      setResultado('Error al crear el encuentro');
    }
  };

  const isLoading = crearSlot.isPending || crearUnico.isPending;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Crear Encuentro</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Creá un encuentro único o un slot recurrente.
        </p>
      </div>

      <div className="flex gap-2 rounded-xl border border-outline-variant bg-surface-container-lowest p-1">
        <button
          onClick={() => setModo('unico')}
          className={`flex-1 rounded-lg px-4 py-2 text-label-sm font-medium transition-colors ${
            modo === 'unico' ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          Encuentro Único
        </button>
        <button
          onClick={() => setModo('recurrente')}
          className={`flex-1 rounded-lg px-4 py-2 text-label-sm font-medium transition-colors ${
            modo === 'recurrente' ? 'bg-primary text-on-primary' : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          Slot Recurrente
        </button>
      </div>

      {resultado && (
        <div className={`rounded-xl border p-4 text-body-sm ${
          resultado.startsWith('¡') ? 'border-success/30 bg-success/5 text-success' : 'border-error/30 bg-error/5 text-error'
        }`}>
          {resultado}
          {resultado.startsWith('¡') && (
            <button
              onClick={() => { setResultado(null); navigate('/encuentros'); }}
              className="ml-2 underline"
            >
              Volver al listado
            </button>
          )}
        </div>
      )}

      {modo === 'recurrente' ? (
        <form onSubmit={recurrenteForm.handleSubmit(onSubmitRecurrente)} className="space-y-4">
          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Materia</label>
            <input
              {...recurrenteForm.register('materia_id')}
              placeholder="ID de la materia"
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
            {recurrenteForm.formState.errors.materia_id && (
              <p className="mt-1 text-label-xs text-error">{recurrenteForm.formState.errors.materia_id.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
            <input
              {...recurrenteForm.register('titulo')}
              placeholder="Ej: Clase teórica"
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
            {recurrenteForm.formState.errors.titulo && (
              <p className="mt-1 text-label-xs text-error">{recurrenteForm.formState.errors.titulo.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">Día de la semana</label>
              <select
                {...recurrenteForm.register('dia_semana', { valueAsNumber: true })}
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
              >
                {DIAS.map((d, i) => (
                  <option key={i} value={i}>{d}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">Cantidad de semanas</label>
              <input
                type="number"
                {...recurrenteForm.register('semanas', { valueAsNumber: true })}
                min={1}
                max={52}
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
              />
              {recurrenteForm.formState.errors.semanas && (
                <p className="mt-1 text-label-xs text-error">{recurrenteForm.formState.errors.semanas.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">Hora inicio</label>
              <input
                type="time"
                {...recurrenteForm.register('hora_inicio')}
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">Hora fin</label>
              <input
                type="time"
                {...recurrenteForm.register('hora_fin')}
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">URL Meet (opcional)</label>
            <input
              {...recurrenteForm.register('url_meet')}
              placeholder="https://meet.google.com/..."
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
            {recurrenteForm.formState.errors.url_meet && (
              <p className="mt-1 text-label-xs text-error">{recurrenteForm.formState.errors.url_meet.message}</p>
            )}
          </div>

          <Button
            type="submit"
            variant="primary"
            disabled={isLoading}
          >
            Generar Slot Recurrente
          </Button>
        </form>
      ) : (
        <form onSubmit={unicoForm.handleSubmit(onSubmitUnico)} className="space-y-4">
          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Materia</label>
            <input
              {...unicoForm.register('materia_id')}
              placeholder="ID de la materia"
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
            {unicoForm.formState.errors.materia_id && (
              <p className="mt-1 text-label-xs text-error">{unicoForm.formState.errors.materia_id.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
            <input
              {...unicoForm.register('titulo')}
              placeholder="Ej: Consulta pre-parcial"
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
            {unicoForm.formState.errors.titulo && (
              <p className="mt-1 text-label-xs text-error">{unicoForm.formState.errors.titulo.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">Fecha</label>
            <input
              type="date"
              {...unicoForm.register('fecha')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
            />
            {unicoForm.formState.errors.fecha && (
              <p className="mt-1 text-label-xs text-error">{unicoForm.formState.errors.fecha.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">Hora inicio</label>
              <input
                type="time"
                {...unicoForm.register('hora_inicio')}
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
              />
            </div>
            <div>
              <label className="mb-1 block text-label-sm text-on-surface-variant">Hora fin</label>
              <input
                type="time"
                {...unicoForm.register('hora_fin')}
                className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-label-sm text-on-surface-variant">URL Meet (opcional)</label>
            <input
              {...unicoForm.register('url_meet')}
              placeholder="https://meet.google.com/..."
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
            />
            {unicoForm.formState.errors.url_meet && (
              <p className="mt-1 text-label-xs text-error">{unicoForm.formState.errors.url_meet.message}</p>
            )}
          </div>

          <Button
            type="submit"
            variant="primary"
            disabled={isLoading}
          >
            Crear Encuentro
          </Button>
        </form>
      )}
    </div>
  );
}
