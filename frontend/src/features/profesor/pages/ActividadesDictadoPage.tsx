import { useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  useActividadesDictado,
  useCalificacionesDictado,
  usePadronDictado,
  useMutationCrearActividad,
  useMutationEditarCalificacion,
  useMutationSubirCalificacionesCsv,
  useMutationRegistrarCalificacion,
} from '../hooks/useProfesor';
import { downloadPlantillaCsv } from '../services/profesor.service';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button } from '@/shared/components/ds';
import type { Actividad, ActividadCreate, CalificacionResponse, CsvUploadResult, EntradaPadron, RegistrarCalificacionData } from '../types';

// ---------- Types ----------

interface EditState {
  calificacionId: string;
  nota: string;
  aprobado: boolean | null;
}

interface VirtualActividad {
  id: string | null;
  nombre: string;
  tipo: string | null;
  fecha_limite: string | null;
}

// ---------- Helpers ----------

function buildVirtualActividades(actividades: Actividad[], calificaciones: CalificacionResponse[]): VirtualActividad[] {
  const result: VirtualActividad[] = actividades.map((a) => ({
    id: a.id, nombre: a.nombre, tipo: a.tipo, fecha_limite: a.fecha_limite,
  }));
  const knownNombres = new Set(actividades.map((a) => a.nombre));
  for (const cal of calificaciones) {
    if (!knownNombres.has(cal.actividad)) {
      knownNombres.add(cal.actividad);
      result.push({ id: null, nombre: cal.actividad, tipo: null, fecha_limite: null });
    }
  }
  return result;
}

function matchGrade(cal: CalificacionResponse, act: VirtualActividad): boolean {
  if (act.id !== null && cal.actividad_id === act.id) return true;
  if (cal.actividad_id === null && cal.actividad === act.nombre) return true;
  if (act.id !== null && cal.actividad_id === null && cal.actividad === act.nombre) return true;
  return false;
}

function alumnoLabel(cal: CalificacionResponse, padron: EntradaPadron[]): string {
  const ep = padron.find((e) => e.id === cal.entrada_padron_id);
  return ep ? `${ep.nombre} ${ep.apellidos}` : cal.entrada_padron_id.slice(0, 8);
}

/** Returns alumnos from padron NOT already graded in this activity */
function ungradedAlumnos(padron: EntradaPadron[], cals: CalificacionResponse[]): EntradaPadron[] {
  const gradedIds = new Set(cals.map((c) => c.entrada_padron_id));
  return padron.filter((ep) => !gradedIds.has(ep.id));
}

// ---------- DS-style Aprobado toggle ----------

/**
 * Design-system styled "Aprobado" toggle.
 * Replaces the bare native <input type="checkbox"> in both create-row and edit-row.
 */
function AprobadoToggle({
  checked,
  onChange,
  id,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  id?: string;
}) {
  return (
    <button
      type="button"
      id={id}
      role="checkbox"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={[
        'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-label-xs font-medium transition-colors',
        checked
          ? 'bg-[color-mix(in_srgb,var(--success)_15%,transparent)] text-[var(--success)]'
          : 'bg-[color-mix(in_srgb,var(--error)_10%,transparent)] text-[var(--error)]',
      ].join(' ')}
    >
      <span className="material-symbols-outlined text-[13px]">
        {checked ? 'check_circle' : 'cancel'}
      </span>
      {checked ? 'Aprobado' : 'Desaprobado'}
    </button>
  );
}

// ---------- CrearActividadModal ----------

const actividadSchema = z.object({
  nombre: z.string().min(1, 'Requerido'),
  tipo: z.string().min(1, 'Requerido'),
  fecha_limite: z.string().optional(),
});

type ActividadForm = z.infer<typeof actividadSchema>;

function CrearActividadModal({ dictadoId, onClose }: { dictadoId: string; onClose: () => void }) {
  const mutation = useMutationCrearActividad(dictadoId);
  const { register, handleSubmit, formState: { errors } } = useForm<ActividadForm>({
    resolver: zodResolver(actividadSchema),
    defaultValues: { nombre: '', tipo: 'tarea', fecha_limite: '' },
  });

  const onSubmit = async (values: ActividadForm) => {
    const payload: ActividadCreate = {
      nombre: values.nombre,
      tipo: values.tipo,
      fecha_limite: values.fecha_limite || null,
    };
    await mutation.mutateAsync(payload);
    onClose();
  };

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-4 space-y-3">
      <h4 style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>Nueva actividad</h4>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div>
            <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Nombre *</label>
            <input {...register('nombre')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary" />
            {errors.nombre && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.nombre.message}</p>}
          </div>
          <div>
            <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Tipo *</label>
            <select {...register('tipo')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary">
              <option value="tarea">Tarea</option>
              <option value="examen">Examen</option>
              <option value="tp">Trabajo Práctico</option>
              <option value="parcial">Parcial</option>
              <option value="coloquio">Coloquio</option>
              <option value="otro">Otro</option>
            </select>
            {errors.tipo && <p style={{ margin: '4px 0 0', fontSize: 12, color: 'var(--error)' }}>{errors.tipo.message}</p>}
          </div>
          <div>
            <label style={{ fontSize: 12, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 4 }}>Fecha límite</label>
            <input type="date" {...register('fecha_limite')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-label-sm text-on-surface outline-none focus:border-primary" />
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
            {mutation.isPending ? 'Guardando…' : 'Crear actividad'}
          </Button>
          <Button type="button" variant="secondary" size="sm" onClick={onClose}>Cancelar</Button>
        </div>
        {mutation.isError && <p style={{ fontSize: 13, color: 'var(--error)' }}>Error al crear la actividad</p>}
      </form>
    </div>
  );
}

// ---------- CsvUpload ----------

function CsvUpload({ actividadId, dictadoId }: { actividadId: string; dictadoId: string }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const mutation = useMutationSubirCalificacionesCsv();
  const [result, setResult] = useState<CsvUploadResult | null>(null);

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const res = await mutation.mutateAsync({ actividadId, file, dictadoId });
      setResult(res);
    } catch {
      // handled via mutation.isError
    }
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
      <input ref={inputRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={handleChange} aria-label="Subir CSV de calificaciones" />
      <Button variant="secondary" size="sm" onClick={() => inputRef.current?.click()} disabled={mutation.isPending}>
        <span className="material-symbols-outlined text-[14px]">upload_file</span>
        {mutation.isPending ? 'Subiendo…' : 'Subir CSV'}
      </Button>
      {result && (
        <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>
          +{result.created} creados, ~{result.updated} actualizados
          {result.errors > 0 && <span style={{ color: 'var(--error)' }}>, {result.errors} errores</span>}
        </span>
      )}
      {mutation.isError && <span style={{ fontSize: 12, color: 'var(--error)' }}>Error al subir CSV</span>}
    </div>
  );
}

// ---------- RegistrarNotaInlineRow ----------

const registrarNotaSchema = z.object({
  entrada_padron_id: z.string().uuid('Seleccioná un alumno'),
  nota_numerica: z.string().optional(),
  nota_textual: z.string().optional(),
  aprobado: z.boolean(),
});

type RegistrarNotaForm = z.infer<typeof registrarNotaSchema>;

/**
 * Inline new-row inside the activity table for registering a grade.
 * Shows ONLY alumnos not already graded in this activity (task 7.2).
 * Rendered as a <tr> so it fits naturally inside the existing <table>.
 */
function RegistrarNotaInlineRow({
  actividadId,
  dictadoId,
  ungraded,
  onClose,
}: {
  actividadId: string;
  dictadoId: string;
  /** Alumnos NOT yet graded in this activity */
  ungraded: EntradaPadron[];
  onClose: () => void;
}) {
  const mutation = useMutationRegistrarCalificacion(dictadoId);
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<RegistrarNotaForm>({
    resolver: zodResolver(registrarNotaSchema),
    defaultValues: { entrada_padron_id: '', nota_numerica: '', nota_textual: '', aprobado: false },
  });
  const aprobadoValue = watch('aprobado');

  const onSubmit = async (values: RegistrarNotaForm) => {
    const payload: RegistrarCalificacionData = {
      entrada_padron_id: values.entrada_padron_id,
      nota_numerica: values.nota_numerica ? parseFloat(values.nota_numerica) : null,
      nota_textual: values.nota_textual || null,
      aprobado: values.aprobado,
    };
    await mutation.mutateAsync({ actividadId, data: payload });
    onClose();
  };

  if (ungraded.length === 0) {
    return (
      <tr className="border-b border-outline-variant bg-surface-container-lowest">
        <td colSpan={4} className="px-4 py-3 text-body-sm text-on-surface-variant text-center">
          Todos los alumnos ya tienen nota en esta actividad
          <Button variant="ghost" size="sm" onClick={onClose} className="ml-3">Cerrar</Button>
        </td>
      </tr>
    );
  }

  return (
    <tr className="border-b border-outline-variant bg-surface-container-lowest" data-testid="registrar-nota-inline-row">
      <td className="px-4 py-2">
        <select
          {...register('entrada_padron_id')}
          className="w-full rounded-lg border border-outline-variant bg-surface-container px-2 py-1.5 text-label-sm text-on-surface outline-none focus:border-primary"
          aria-label="Alumno"
        >
          <option value="">— Alumno —</option>
          {ungraded.map((ep) => (
            <option key={ep.id} value={ep.id}>
              {ep.apellidos}, {ep.nombre}
            </option>
          ))}
        </select>
        {errors.entrada_padron_id && (
          <p style={{ margin: '2px 0 0', fontSize: 11, color: 'var(--error)' }}>{errors.entrada_padron_id.message}</p>
        )}
      </td>
      <td className="px-4 py-2">
        <input
          type="number"
          step="0.01"
          {...register('nota_numerica')}
          placeholder="Nota"
          className="w-20 rounded border border-outline-variant bg-surface-container px-2 py-1 text-body-sm text-on-surface outline-none focus:border-primary"
          aria-label="Nota numérica"
        />
      </td>
      <td className="px-4 py-2">
        <AprobadoToggle
          checked={aprobadoValue}
          onChange={(v) => setValue('aprobado', v)}
          id={`aprobado-new-${actividadId}`}
        />
      </td>
      <td className="px-4 py-2">
        <div style={{ display: 'flex', gap: 4 }}>
          <Button
            type="button"
            variant="primary"
            size="sm"
            onClick={handleSubmit(onSubmit)}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? '…' : 'Guardar'}
          </Button>
          <Button type="button" variant="secondary" size="sm" onClick={onClose}>Cancelar</Button>
        </div>
        {mutation.isError && <p style={{ fontSize: 11, color: 'var(--error)', marginTop: 2 }}>Error</p>}
      </td>
    </tr>
  );
}

// ---------- ActividadCard ----------

function ActividadCard({
  act,
  dictadoId,
  cals,
  padron,
  editState,
  onStartEdit,
  onSave,
  onCancelEdit,
  onChangeEdit,
  isSaving,
  isRegistrando,
  onRegistrarNota,
  onCloseRegistrar,
}: {
  act: VirtualActividad;
  dictadoId: string;
  cals: CalificacionResponse[];
  padron: EntradaPadron[];
  editState: EditState | null;
  onStartEdit: (state: EditState) => void;
  onSave: () => void;
  onCancelEdit: () => void;
  onChangeEdit: (partial: Partial<EditState>) => void;
  isSaving: boolean;
  /** Whether the inline registrar-nota row is open for THIS activity */
  isRegistrando: boolean;
  onRegistrarNota?: (actividadId: string) => void;
  onCloseRegistrar: () => void;
}) {
  const key = act.id ?? `legacy-${act.nombre}`;
  const ungraded = ungradedAlumnos(padron, cals);

  return (
    <div key={key} className="rounded-xl border border-outline-variant overflow-hidden">
      <div className="bg-surface-container-low px-4 py-3 flex items-center gap-3 flex-wrap">
        <span className="material-symbols-outlined text-[18px] text-on-surface-variant">assignment</span>
        <span style={{ fontWeight: 600, color: 'var(--on-surface)', fontSize: 15 }}>{act.nombre}</span>
        {act.tipo && <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>({act.tipo})</span>}
        {act.id === null && <span style={{ fontSize: 11, color: 'var(--outline)', marginLeft: 4 }}>importada</span>}
        {act.fecha_limite && (
          <span style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginLeft: 'auto' }}>
            Límite: {act.fecha_limite}
          </span>
        )}
        {act.id !== null && (
          <div style={{ display: 'flex', gap: 6, marginLeft: act.fecha_limite ? undefined : 'auto', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => downloadPlantillaCsv(act.id!, `plantilla_${act.nombre}.csv`)}
              className="inline-flex items-center gap-1 rounded-lg bg-surface-container px-2 py-1 text-label-xs text-on-surface-variant transition-colors hover:bg-surface-container-high"
              title="Descarga la plantilla CSV prefilled con las notas actuales"
            >
              <span className="material-symbols-outlined text-[13px]">download</span>
              Plantilla CSV
            </button>
            <CsvUpload actividadId={act.id} dictadoId={dictadoId} />
            {onRegistrarNota && !isRegistrando && (
              <Button variant="secondary" size="sm" onClick={() => onRegistrarNota(act.id!)}>
                <span className="material-symbols-outlined text-[14px]">add_circle</span>
                Registrar nota
              </Button>
            )}
          </div>
        )}
      </div>

      {cals.length === 0 && !isRegistrando ? (
        <div className="px-4 py-6 text-body-sm text-on-surface-variant text-center">Sin calificaciones registradas</div>
      ) : (
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-outline-variant">
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Alumno</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Nota</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Aprobado</th>
              <th className="px-4 py-2 text-label-sm font-medium text-on-surface-variant">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {cals.map((cal) => {
              const isEditing = editState?.calificacionId === cal.id;
              return (
                <tr key={cal.id} className="border-b border-outline-variant hover:bg-surface-container-low">
                  <td className="px-4 py-2 text-body-sm text-on-surface">{alumnoLabel(cal, padron)}</td>
                  <td className="px-4 py-2 text-body-sm text-on-surface-variant">
                    {isEditing ? (
                      <input
                        type="number"
                        value={editState.nota}
                        onChange={(e) => onChangeEdit({ nota: e.target.value })}
                        className="w-20 rounded border border-outline-variant bg-surface-container px-2 py-1 text-body-sm text-on-surface outline-none focus:border-primary"
                      />
                    ) : (
                      cal.nota_numerica !== null ? String(cal.nota_numerica) : '—'
                    )}
                  </td>
                  <td className="px-4 py-2">
                    {isEditing ? (
                      <AprobadoToggle
                        checked={editState.aprobado ?? false}
                        onChange={(v) => onChangeEdit({ aprobado: v })}
                        id={`aprobado-edit-${cal.id}`}
                      />
                    ) : (
                      <span style={{ fontSize: 13, color: cal.aprobado ? 'var(--success)' : 'var(--error)' }}>
                        {cal.aprobado === null ? '—' : cal.aprobado ? 'Sí' : 'No'}
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-2">
                    {isEditing ? (
                      <div style={{ display: 'flex', gap: 4 }}>
                        <Button variant="primary" size="sm" onClick={onSave} disabled={isSaving}>Guardar</Button>
                        <Button variant="secondary" size="sm" onClick={onCancelEdit}>Cancelar</Button>
                      </div>
                    ) : (
                      <Button variant="ghost" size="sm" onClick={() => onStartEdit({ calificacionId: cal.id, nota: cal.nota_numerica !== null ? String(cal.nota_numerica) : '', aprobado: cal.aprobado })}>
                        <span className="material-symbols-outlined text-[14px]">edit</span>
                        Editar
                      </Button>
                    )}
                  </td>
                </tr>
              );
            })}
            {/* Inline registrar-nota row — rendered INSIDE this activity's table (task 7) */}
            {isRegistrando && act.id !== null && (
              <RegistrarNotaInlineRow
                actividadId={act.id}
                dictadoId={dictadoId}
                ungraded={ungraded}
                onClose={onCloseRegistrar}
              />
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ---------- Main Page ----------

export function ActividadesDictadoPage() {
  const { dictadoId } = useParams<{ dictadoId: string }>();
  const [showCrear, setShowCrear] = useState(false);
  const [editState, setEditState] = useState<EditState | null>(null);
  const [registrarNotaActividadId, setRegistrarNotaActividadId] = useState<string | null>(null);

  const { data: actividades, isLoading: loadingActs } = useActividadesDictado(dictadoId!);
  const { data: calificaciones, isLoading: loadingCals } = useCalificacionesDictado(dictadoId!);
  const { data: padron } = usePadronDictado(dictadoId!);
  const editarMutation = useMutationEditarCalificacion();

  const isLoading = loadingActs || loadingCals;

  const virtualActividades = buildVirtualActividades(actividades ?? [], calificaciones ?? []);

  const handleSave = async () => {
    if (!editState) return;
    const nota = editState.nota !== '' ? parseFloat(editState.nota) : null;
    await editarMutation.mutateAsync({
      calificacionId: editState.calificacionId,
      data: { nota_numerica: nota, aprobado: editState.aprobado ?? undefined },
    });
    setEditState(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: 'var(--on-surface)' }}>Actividades</h3>
        <Button variant="primary" size="sm" onClick={() => setShowCrear((v) => !v)}>
          <span className="material-symbols-outlined text-[16px]">add</span>
          Crear actividad
        </Button>
      </div>

      {showCrear && <CrearActividadModal dictadoId={dictadoId!} onClose={() => setShowCrear(false)} />}

      {isLoading ? (
        <LoadingState rows={5} cols={4} />
      ) : virtualActividades.length === 0 ? (
        <EmptyState message="No hay actividades ni calificaciones en este dictado" icon="assignment" />
      ) : (
        <div className="space-y-8">
          {virtualActividades.map((act) => (
            <ActividadCard
              key={act.id ?? `legacy-${act.nombre}`}
              act={act}
              dictadoId={dictadoId!}
              cals={(calificaciones ?? []).filter((c) => matchGrade(c, act))}
              padron={padron ?? []}
              editState={editState}
              onStartEdit={setEditState}
              onSave={handleSave}
              onCancelEdit={() => setEditState(null)}
              onChangeEdit={(partial) => setEditState((s) => s ? { ...s, ...partial } : s)}
              isSaving={editarMutation.isPending}
              isRegistrando={registrarNotaActividadId === act.id}
              onRegistrarNota={(actividadId) => setRegistrarNotaActividadId(actividadId)}
              onCloseRegistrar={() => setRegistrarNotaActividadId(null)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
