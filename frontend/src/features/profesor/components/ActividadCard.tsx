/**
 * ActividadCard — displays a single actividad with its calificaciones table,
 * inline registrar-nota row, CSV upload, and edit/delete controls.
 *
 * Extracted from ActividadesDictadoPage to keep each file under 200 LOC.
 */
import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  useMutationSubirCalificacionesCsv,
  useMutationRegistrarCalificacion,
} from '../hooks/useProfesor';
import { downloadPlantillaCsv } from '../services/profesor.service';
import { getFechaLimiteStatus } from '../utils/fechaLimiteStatus';
import { Button } from '@/shared/components/ds';
import type { Actividad, CalificacionResponse, CsvUploadResult, EntradaPadron, RegistrarCalificacionData } from '../types';

// ---------- Types (shared with parent page) ----------

export interface EditState {
  calificacionId: string;
  nota: string;
  aprobado: boolean | null;
}

export interface VirtualActividad {
  id: string | null;
  nombre: string;
  tipo: string | null;
  fecha_limite: string | null;
}

// ---------- Helpers ----------

export function buildVirtualActividades(actividades: Actividad[], calificaciones: CalificacionResponse[]): VirtualActividad[] {
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

export function matchGrade(cal: CalificacionResponse, act: VirtualActividad): boolean {
  if (act.id !== null && cal.actividad_id === act.id) return true;
  if (cal.actividad_id === null && cal.actividad === act.nombre) return true;
  if (act.id !== null && cal.actividad_id === null && cal.actividad === act.nombre) return true;
  return false;
}

export function alumnoLabel(cal: CalificacionResponse, padron: EntradaPadron[]): string {
  const ep = padron.find((e) => e.id === cal.entrada_padron_id);
  return ep ? `${ep.nombre} ${ep.apellidos}` : cal.entrada_padron_id.slice(0, 8);
}

export function ungradedAlumnos(padron: EntradaPadron[], cals: CalificacionResponse[]): EntradaPadron[] {
  const gradedIds = new Set(cals.map((c) => c.entrada_padron_id));
  return padron.filter((ep) => !gradedIds.has(ep.id));
}

// ---------- AprobadoToggle ----------

export function AprobadoToggle({ checked, onChange, id }: { checked: boolean; onChange: (v: boolean) => void; id?: string }) {
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
      <span className="material-symbols-outlined text-[13px]">{checked ? 'check_circle' : 'cancel'}</span>
      {checked ? 'Aprobado' : 'Desaprobado'}
    </button>
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
    try { const res = await mutation.mutateAsync({ actividadId, file, dictadoId }); setResult(res); } catch { /* handled via mutation.isError */ }
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
      <input ref={inputRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={handleChange} aria-label="Subir CSV de calificaciones" />
      <Button variant="secondary" size="sm" onClick={() => inputRef.current?.click()} disabled={mutation.isPending}>
        <span className="material-symbols-outlined text-[14px]">upload_file</span>
        {mutation.isPending ? 'Subiendo…' : 'Subir CSV'}
      </Button>
      {result && <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>+{result.created} creados, ~{result.updated} actualizados{result.errors > 0 && <span style={{ color: 'var(--error)' }}>, {result.errors} errores</span>}</span>}
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

function RegistrarNotaInlineRow({ actividadId, dictadoId, ungraded, onClose }: { actividadId: string; dictadoId: string; ungraded: EntradaPadron[]; onClose: () => void }) {
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

  if (ungraded.length === 0) return (
    <tr className="border-b border-outline-variant bg-surface-container-lowest">
      <td colSpan={4} className="px-4 py-3 text-body-sm text-on-surface-variant text-center">
        Todos los alumnos ya tienen nota<Button variant="ghost" size="sm" onClick={onClose} className="ml-3">Cerrar</Button>
      </td>
    </tr>
  );

  return (
    <tr className="border-b border-outline-variant bg-surface-container-lowest" data-testid="registrar-nota-inline-row">
      <td className="px-4 py-2">
        <select {...register('entrada_padron_id')} className="w-full rounded-lg border border-outline-variant bg-surface-container px-2 py-1.5 text-label-sm text-on-surface outline-none focus:border-primary" aria-label="Alumno">
          <option value="">— Alumno —</option>
          {ungraded.map((ep) => <option key={ep.id} value={ep.id}>{ep.apellidos}, {ep.nombre}</option>)}
        </select>
        {errors.entrada_padron_id && <p style={{ margin: '2px 0 0', fontSize: 11, color: 'var(--error)' }}>{errors.entrada_padron_id.message}</p>}
      </td>
      <td className="px-4 py-2">
        <input type="number" step="0.01" {...register('nota_numerica')} placeholder="Nota" className="w-20 rounded border border-outline-variant bg-surface-container px-2 py-1 text-body-sm text-on-surface outline-none focus:border-primary" aria-label="Nota numérica" />
      </td>
      <td className="px-4 py-2">
        <AprobadoToggle checked={aprobadoValue} onChange={(v) => setValue('aprobado', v)} id={`aprobado-new-${actividadId}`} />
      </td>
      <td className="px-4 py-2">
        <div style={{ display: 'flex', gap: 4 }}>
          <Button type="button" variant="primary" size="sm" onClick={handleSubmit(onSubmit)} disabled={mutation.isPending}>{mutation.isPending ? '…' : 'Guardar'}</Button>
          <Button type="button" variant="secondary" size="sm" onClick={onClose}>Cancelar</Button>
        </div>
        {mutation.isError && <p style={{ fontSize: 11, color: 'var(--error)', marginTop: 2 }}>Error</p>}
      </td>
    </tr>
  );
}

// ---------- ActividadCard ----------

export function ActividadCard({
  act, dictadoId, cals, padron, editState, onStartEdit, onSave, onCancelEdit, onChangeEdit, isSaving,
  isRegistrando, onRegistrarNota, onCloseRegistrar, onEditActividad, onEliminarActividad,
}: {
  act: VirtualActividad; dictadoId: string; cals: CalificacionResponse[]; padron: EntradaPadron[];
  editState: EditState | null; onStartEdit: (state: EditState) => void; onSave: () => void;
  onCancelEdit: () => void; onChangeEdit: (partial: Partial<EditState>) => void; isSaving: boolean;
  isRegistrando: boolean; onRegistrarNota?: (actividadId: string) => void; onCloseRegistrar: () => void;
  onEditActividad?: (act: Actividad) => void; onEliminarActividad?: (actividadId: string) => void;
}) {
  const ungraded = ungradedAlumnos(padron, cals);
  const fechaStatus = getFechaLimiteStatus(act.fecha_limite);

  return (
    <div className="rounded-xl border border-outline-variant overflow-hidden">
      <div className="bg-surface-container-low px-4 py-3 flex items-center gap-3 flex-wrap">
        <span className="material-symbols-outlined text-[18px] text-on-surface-variant">assignment</span>
        <span style={{ fontWeight: 600, color: 'var(--on-surface)', fontSize: 15 }}>{act.nombre}</span>
        {act.tipo && <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>({act.tipo})</span>}
        {act.fecha_limite && (
          <span style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>Límite: {act.fecha_limite}</span>
        )}
        {fechaStatus === 'vencida' && (
          <span className="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium bg-[color-mix(in_srgb,var(--error)_12%,transparent)] text-[var(--error)]">
            Vencida
          </span>
        )}
        {fechaStatus === 'proxima' && (
          <span className="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium bg-[color-mix(in_srgb,var(--primary)_12%,transparent)] text-[var(--primary)]">
            Próxima
          </span>
        )}
        {act.id === null && <span style={{ fontSize: 11, color: 'var(--outline)', marginLeft: 4 }}>importada</span>}
        {act.id !== null && (
          <div style={{ display: 'flex', gap: 6, marginLeft: 'auto', flexWrap: 'wrap' }}>
            <button type="button" onClick={() => downloadPlantillaCsv(act.id!, `plantilla_${act.nombre}.csv`)} className="inline-flex items-center gap-1 rounded-lg bg-surface-container px-2 py-1 text-label-xs text-on-surface-variant transition-colors hover:bg-surface-container-high" title="Descarga la plantilla CSV prefilled con las notas actuales">
              <span className="material-symbols-outlined text-[13px]">download</span>Plantilla CSV
            </button>
            <CsvUpload actividadId={act.id} dictadoId={dictadoId} />
            {onRegistrarNota && !isRegistrando && (
              <Button variant="secondary" size="sm" onClick={() => onRegistrarNota(act.id!)}>
                <span className="material-symbols-outlined text-[14px]">add_circle</span>
                Registrar nota
              </Button>
            )}
            {onEditActividad && (
              <Button variant="secondary" size="sm" aria-label={`Editar actividad ${act.nombre}`}
                onClick={() => onEditActividad({ id: act.id!, nombre: act.nombre, tipo: act.tipo ?? '', fecha_limite: act.fecha_limite })}>
                <span className="material-symbols-outlined text-[14px]">edit</span>Editar actividad
              </Button>
            )}
            {onEliminarActividad && (
              <Button variant="ghost" size="sm" aria-label={`Eliminar actividad ${act.nombre}`} onClick={() => onEliminarActividad(act.id!)}>
                <span className="material-symbols-outlined text-[14px]">delete</span>Eliminar
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
                    {isEditing ? <input type="number" value={editState.nota} onChange={(e) => onChangeEdit({ nota: e.target.value })} className="w-20 rounded border border-outline-variant bg-surface-container px-2 py-1 text-body-sm text-on-surface outline-none focus:border-primary" />
                      : (cal.nota_numerica !== null ? String(cal.nota_numerica) : '—')}
                  </td>
                  <td className="px-4 py-2">
                    {isEditing
                      ? <AprobadoToggle checked={editState.aprobado ?? false} onChange={(v) => onChangeEdit({ aprobado: v })} id={`aprobado-edit-${cal.id}`} />
                      : <span style={{ fontSize: 13, color: cal.aprobado ? 'var(--success)' : 'var(--error)' }}>{cal.aprobado === null ? '—' : cal.aprobado ? 'Sí' : 'No'}</span>}
                  </td>
                  <td className="px-4 py-2">
                    {isEditing ? (
                      <div style={{ display: 'flex', gap: 4 }}>
                        <Button variant="primary" size="sm" onClick={onSave} disabled={isSaving}>Guardar</Button>
                        <Button variant="secondary" size="sm" onClick={onCancelEdit}>Cancelar</Button>
                      </div>
                    ) : (
                      <Button variant="ghost" size="sm" onClick={() => onStartEdit({ calificacionId: cal.id, nota: cal.nota_numerica !== null ? String(cal.nota_numerica) : '', aprobado: cal.aprobado })}>
                        <span className="material-symbols-outlined text-[14px]">edit</span>Editar
                      </Button>
                    )}
                  </td>
                </tr>
              );
            })}
            {isRegistrando && act.id !== null && (
              <RegistrarNotaInlineRow actividadId={act.id} dictadoId={dictadoId} ungraded={ungraded} onClose={onCloseRegistrar} />
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
