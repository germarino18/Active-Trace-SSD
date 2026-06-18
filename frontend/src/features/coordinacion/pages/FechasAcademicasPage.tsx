import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  useFechasAcademicas,
  useCrearFechaAcademica,
  useActualizarFechaAcademica,
  useGenerarHtmlFechas,
} from '../hooks/useProgramas';
import { CalendarioFechas } from '../components/CalendarioFechas';
import { DataTable, type ColumnDef } from '../components/DataTable';
import { HelpButton } from '../components/HelpButton';
import { useAuth } from '@/features/auth/hooks/useAuth';
import type { FechaAcademica, TipoFechaAcademica } from '../types';

const fechaSchema = z.object({
  materia_id: z.string().min(1, 'La materia es requerida'),
  cohorte_id: z.string().min(1, 'La cohorte es requerida'),
  tipo: z.enum(['Parcial', 'TP', 'Coloquio']),
  instancia: z.coerce.number().min(1, 'La instancia debe ser ≥ 1'),
  titulo: z.string().min(1, 'El título es requerido'),
  fecha: z.string().min(1, 'La fecha es requerida'),
});

type FechaForm = z.infer<typeof fechaSchema>;

const tipoBadge: Record<TipoFechaAcademica, string> = {
  Parcial: 'bg-blue-500/10 text-blue-600',
  TP: 'bg-green-500/10 text-green-600',
  Coloquio: 'bg-purple-500/10 text-purple-600',
};

export function FechasAcademicasPage() {
  const { hasPermission } = useAuth();
  const [viewMode, setViewMode] = useState<'tabla' | 'calendario'>('tabla');
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [editingId, setEditingId] = useState<string | null>(null);
  const [htmlModal, setHtmlModal] = useState<{ html: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const { data: fechas, isLoading } = useFechasAcademicas();
  const crearFecha = useCrearFechaAcademica();
  const actualizarFecha = useActualizarFechaAcademica();
  const generarHtml = useGenerarHtmlFechas();

  const canManage = hasPermission('coordinacion:fechas:gestionar');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FechaForm>({
    resolver: zodResolver(fechaSchema),
    defaultValues: {
      materia_id: '',
      cohorte_id: '',
      tipo: 'Parcial',
      instancia: 1,
      titulo: '',
      fecha: '',
    },
  });

  const onSubmit = async (data: FechaForm) => {
    try {
      await crearFecha.mutateAsync(data);
      reset();
    } catch {
      // handled by mutation error state
    }
  };

  const handleEditSave = async (id: string, data: Partial<FechaForm>) => {
    try {
      await actualizarFecha.mutateAsync({ id, data });
      setEditingId(null);
    } catch {
      // handled by mutation error state
    }
  };

  const handleGenerarHtml = async () => {
    if (!fechas || fechas.length === 0) return;
    const first = fechas[0];
    try {
      const result = await generarHtml.mutateAsync({
        materiaId: first.materia_id,
        cohorteId: first.cohorte_id,
      });
      setHtmlModal(result);
    } catch {
      // handled by mutation error state
    }
  };

  const handleCopyHtml = async () => {
    if (!htmlModal) return;
    try {
      await navigator.clipboard.writeText(htmlModal.html);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignored
    }
  };

  const columns: ColumnDef<FechaAcademica>[] = [
    { key: 'titulo', label: 'Título' },
    { key: 'materia_nombre', label: 'Materia' },
    { key: 'cohorte_nombre', label: 'Cohorte' },
    {
      key: 'tipo',
      label: 'Tipo',
      render: (row) => (
        <span className={`inline-flex rounded-full px-2.5 py-0.5 text-label-xs font-medium ${tipoBadge[row.tipo]}`}>
          {row.tipo}
        </span>
      ),
    },
    {
      key: 'instancia',
      label: 'Instancia',
      render: (row) => `N° ${row.instancia}`,
    },
    {
      key: 'fecha',
      label: 'Fecha',
      render: (row) => new Date(row.fecha).toLocaleDateString('es-AR'),
    },
    ...(canManage
      ? [
          {
            key: 'acciones' as const,
            label: 'Acciones',
            render: (row: FechaAcademica) => (
              <button
                type="button"
                onClick={() => setEditingId(row.id)}
                className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                title="Editar"
              >
                <span className="material-symbols-outlined text-[18px]">edit</span>
              </button>
            ),
          },
        ]
      : []),
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Fechas Académicas</h2>
            <p className="text-body-md text-on-surface-variant mt-1">
              Gestioná las fechas de parciales, TP y coloquios.
            </p>
          </div>
          <HelpButton tooltip="Administrá el calendario de fechas académicas. Podés alternar entre vista de tabla y calendario." />
        </div>
        <div className="flex items-center gap-2">
          <div className="flex rounded-lg border border-outline-variant overflow-hidden">
            <button
              type="button"
              onClick={() => setViewMode('tabla')}
              className={`px-3 py-1.5 text-label-sm transition-colors ${
                viewMode === 'tabla'
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container-low'
              }`}
            >
              Tabla
            </button>
            <button
              type="button"
              onClick={() => setViewMode('calendario')}
              className={`px-3 py-1.5 text-label-sm transition-colors ${
                viewMode === 'calendario'
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container-lowest text-on-surface-variant hover:bg-surface-container-low'
              }`}
            >
              Calendario
            </button>
          </div>
          {fechas && fechas.length > 0 && (
            <button
              type="button"
              onClick={handleGenerarHtml}
              disabled={generarHtml.isPending}
              className="inline-flex items-center gap-1.5 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low disabled:opacity-50"
            >
              <span className="material-symbols-outlined text-[18px]">code</span>
              Generar contenido aula virtual
            </button>
          )}
        </div>
      </div>

      {viewMode === 'tabla' ? (
        <>
          <DataTable
            columns={columns}
            data={fechas ?? []}
            rowKey="id"
            isLoading={isLoading}
            emptyMessage="No hay fechas académicas cargadas."
          />

          {canManage && (
            <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-6">
              <h3 className="text-label-md font-medium text-on-surface mb-4">Agregar fecha académica</h3>
              <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="mb-1 block text-label-xs text-on-surface-variant">Materia ID</label>
                  <input {...register('materia_id')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
                  {errors.materia_id && <p className="mt-0.5 text-label-xs text-error">{errors.materia_id.message}</p>}
                </div>
                <div>
                  <label className="mb-1 block text-label-xs text-on-surface-variant">Cohorte ID</label>
                  <input {...register('cohorte_id')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
                  {errors.cohorte_id && <p className="mt-0.5 text-label-xs text-error">{errors.cohorte_id.message}</p>}
                </div>
                <div>
                  <label className="mb-1 block text-label-xs text-on-surface-variant">Tipo</label>
                  <select {...register('tipo')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary">
                    <option value="Parcial">Parcial</option>
                    <option value="TP">TP</option>
                    <option value="Coloquio">Coloquio</option>
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-label-xs text-on-surface-variant">Instancia N°</label>
                  <input type="number" min={1} {...register('instancia')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
                  {errors.instancia && <p className="mt-0.5 text-label-xs text-error">{errors.instancia.message}</p>}
                </div>
                <div>
                  <label className="mb-1 block text-label-xs text-on-surface-variant">Título</label>
                  <input {...register('titulo')} placeholder="Ej: Parcial 1" className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
                  {errors.titulo && <p className="mt-0.5 text-label-xs text-error">{errors.titulo.message}</p>}
                </div>
                <div>
                  <label className="mb-1 block text-label-xs text-on-surface-variant">Fecha</label>
                  <input type="date" {...register('fecha')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
                  {errors.fecha && <p className="mt-0.5 text-label-xs text-error">{errors.fecha.message}</p>}
                </div>
                <div className="sm:col-span-2 lg:col-span-3 flex gap-3">
                  <button
                    type="submit"
                    disabled={crearFecha.isPending}
                    className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
                  >
                    {crearFecha.isPending && (
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />
                    )}
                    <span className="material-symbols-outlined text-[18px]">add</span>
                    Agregar fecha
                  </button>
                </div>
              </form>
            </div>
          )}

          {editingId && fechas && (
            <EditFechaModal
              fecha={fechas.find((f) => f.id === editingId)!}
              onSave={handleEditSave}
              onClose={() => setEditingId(null)}
              isPending={actualizarFecha.isPending}
            />
          )}
        </>
      ) : (
        <CalendarioFechas
          fechas={fechas ?? []}
          currentMonth={currentMonth}
          onMonthChange={setCurrentMonth}
        />
      )}

      {htmlModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => { setHtmlModal(null); setCopied(false); }}
        >
          <div
            className="mx-4 w-full max-w-3xl max-h-[80vh] rounded-xl border border-outline-variant bg-surface p-6 shadow-xl overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-label-md font-medium text-on-surface">Contenido para aula virtual</h3>
              <button
                type="button"
                onClick={handleCopyHtml}
                className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-1.5 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
              >
                <span className="material-symbols-outlined text-[16px]">
                  {copied ? 'check' : 'content_copy'}
                </span>
                {copied ? 'Copiado' : 'Copiar HTML'}
              </button>
            </div>
            <div className="flex-1 overflow-auto rounded-lg border border-outline-variant bg-surface-container-low p-4">
              <pre className="text-body-sm text-on-surface whitespace-pre-wrap font-mono">
                {htmlModal.html}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

interface EditFechaModalProps {
  fecha: FechaAcademica;
  onSave: (id: string, data: Partial<FechaForm>) => void;
  onClose: () => void;
  isPending: boolean;
}

function EditFechaModal({ fecha, onSave, onClose, isPending }: EditFechaModalProps) {
  const { register, handleSubmit } = useForm<Partial<FechaForm>>({
    defaultValues: {
      titulo: fecha.titulo,
      tipo: fecha.tipo,
      instancia: fecha.instancia,
      fecha: fecha.fecha,
    },
  });

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div className="mx-4 w-full max-w-md rounded-xl border border-outline-variant bg-surface p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-label-md font-medium text-on-surface mb-4">Editar fecha académica</h3>
        <form onSubmit={handleSubmit((data) => onSave(fecha.id, data))} className="space-y-4">
          <div>
            <label className="mb-1 block text-label-xs text-on-surface-variant">Título</label>
            <input {...register('titulo')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
          </div>
          <div>
            <label className="mb-1 block text-label-xs text-on-surface-variant">Tipo</label>
            <select {...register('tipo')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary">
              <option value="Parcial">Parcial</option>
              <option value="TP">TP</option>
              <option value="Coloquio">Coloquio</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-label-xs text-on-surface-variant">Instancia N°</label>
            <input type="number" {...register('instancia', { valueAsNumber: true })} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
          </div>
          <div>
            <label className="mb-1 block text-label-xs text-on-surface-variant">Fecha</label>
            <input type="date" {...register('fecha')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm outline-none focus:border-primary" />
          </div>
          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm text-on-surface hover:bg-surface-container-low">
              Cancelar
            </button>
            <button type="submit" disabled={isPending} className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary hover:bg-primary/90 disabled:opacity-50">
              Guardar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
