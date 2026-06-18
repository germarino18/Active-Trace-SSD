import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useCrearPrograma } from '../hooks/useProgramas';

const programaSchema = z.object({
  materia_id: z.string().min(1, 'La materia es requerida'),
  carrera_id: z.string().min(1, 'La carrera es requerida'),
  cohorte_id: z.string().min(1, 'La cohorte es requerida'),
  titulo: z.string().min(1, 'El título es requerido'),
});

type ProgramaForm = z.infer<typeof programaSchema>;

export function ProgramaCrearPage() {
  const navigate = useNavigate();
  const crearPrograma = useCrearPrograma();
  const [file, setFile] = useState<File | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProgramaForm>({
    resolver: zodResolver(programaSchema),
    defaultValues: {
      materia_id: '',
      carrera_id: '',
      cohorte_id: '',
      titulo: '',
    },
  });

  const onSubmit = async (data: ProgramaForm) => {
    if (!file) return;
    try {
      await crearPrograma.mutateAsync({ file, data });
      navigate('/programas');
    } catch {
      // handled by mutation error state
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Subir Programa</h2>
        <p className="text-body-md text-on-surface-variant mt-1">
          Cargá un nuevo programa de estudio en formato PDF.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Archivo PDF</label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface file:mr-3 file:rounded-lg file:border-0 file:bg-primary/10 file:px-3 file:py-1 file:text-label-sm file:text-primary file:cursor-pointer"
          />
          {!file && <p className="mt-1 text-label-xs text-error">Seleccioná un archivo PDF</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
          <input
            {...register('titulo')}
            placeholder="Ej: Programa Analítico 2024"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.titulo && <p className="mt-1 text-label-xs text-error">{errors.titulo.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">ID de Materia</label>
          <input
            {...register('materia_id')}
            placeholder="ID de la materia"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.materia_id && <p className="mt-1 text-label-xs text-error">{errors.materia_id.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">ID de Carrera</label>
          <input
            {...register('carrera_id')}
            placeholder="ID de la carrera"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.carrera_id && <p className="mt-1 text-label-xs text-error">{errors.carrera_id.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">ID de Cohorte</label>
          <input
            {...register('cohorte_id')}
            placeholder="ID de la cohorte"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
          {errors.cohorte_id && <p className="mt-1 text-label-xs text-error">{errors.cohorte_id.message}</p>}
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={crearPrograma.isPending || !file}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {crearPrograma.isPending && (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-on-primary/30 border-t-on-primary" />
            )}
            Subir programa
          </button>
          <button
            type="button"
            onClick={() => navigate('/programas')}
            className="rounded-lg border border-outline-variant px-6 py-2.5 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Cancelar
          </button>
        </div>

        {crearPrograma.isError && (
          <div className="rounded-xl border border-error/30 bg-error/5 p-4 text-body-sm text-error">
            Error al subir el programa. Intentá de nuevo.
          </div>
        )}
      </form>
    </div>
  );
}
