import { useState, useRef, useEffect, useCallback } from 'react';
import { LoadingState } from '@/features/academico/components/LoadingState';
import { EmptyState } from '@/features/academico/components/EmptyState';
import { Button, Input, Select } from '@/shared/components/ds';
import {
  useMaterias,
  useCrearMateria,
  useActualizarMateria,
  useToggleMateriaEstado,
  useCarreras,
  useCohortes,
  useSubirPrograma,
  useEvaluaciones,
  useCrearEvaluacion,
} from '../hooks/useEstructura';
import type { Materia, CrearMateriaData, ActualizarMateriaData, CrearEvaluacionData, Evaluacion } from '../types';

const emptyForm: CrearMateriaData = { nombre: '', codigo: '', carrera_id: '', cohorte_id: '' };

export function MateriasPage() {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { data, isLoading, isError } = useMaterias(debouncedQuery ? { q: debouncedQuery } : undefined);
  const { data: carrerasData } = useCarreras({ activa: true });
  const { data: cohortesData } = useCohortes({ activa: true });
  const crear = useCrearMateria();
  const actualizar = useActualizarMateria();
  const toggleEstado = useToggleMateriaEstado();
  const subirPrograma = useSubirPrograma();
  const crearEvaluacion = useCrearEvaluacion();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedQuery(query);
    }, 300);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query]);

  const [modalOpen, setModalOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Materia | null>(null);
  const [form, setForm] = useState<CrearMateriaData>(emptyForm);
  const [selectedMateria, setSelectedMateria] = useState<Materia | null>(null);

  const { data: evaluacionesData } = useEvaluaciones(selectedMateria?.id);
  const [evForm, setEvForm] = useState<CrearEvaluacionData>({
    materia_id: '', tipo: 'parcial', instancia: 1, fecha: '', titulo: '', cohorte_id: '',
  });

  const fileRef = useRef<HTMLInputElement>(null);
  const [programaTitulo, setProgramaTitulo] = useState('');

  const materias = data?.items ?? [];
  const carreras = carrerasData?.items ?? [];
  const cohortes = cohortesData?.items ?? [];
  const evaluaciones = evaluacionesData?.items ?? [];

  function openCreate() {
    setEditTarget(null);
    setForm(emptyForm);
    setModalOpen(true);
  }

  function openEdit(m: Materia) {
    setEditTarget(m);
    setForm({
      nombre: m.nombre,
      codigo: m.codigo ?? '',
      carrera_id: m.carrera_id ?? '',
      cohorte_id: m.cohorte_id ?? '',
    });
    setModalOpen(true);
  }

  async function handleSubmit() {
    const payload: CrearMateriaData = {
      nombre: form.nombre,
      codigo: form.codigo || undefined,
      carrera_id: form.carrera_id || undefined,
      cohorte_id: form.cohorte_id || undefined,
    };
    try {
      if (editTarget) {
        await actualizar.mutateAsync({ id: editTarget.id, data: payload as ActualizarMateriaData });
      } else {
        await crear.mutateAsync(payload);
      }
      setModalOpen(false);
      setSelectedMateria(null);
    } catch {
      // Error is handled by the mutation — modal stays open for retry
    }
  }

  function handleSelectMateria(m: Materia) {
    setSelectedMateria(m);
    setEvForm({
      materia_id: m.id, tipo: 'parcial', instancia: 1, fecha: '', titulo: '', cohorte_id: m.cohorte_id ?? '',
    });
    setProgramaTitulo('');
    if (fileRef.current) fileRef.current.value = '';
  }

  function handleSubirPrograma() {
    if (!selectedMateria || !fileRef.current?.files?.[0]) return;
    subirPrograma.mutate(
      { materiaId: selectedMateria.id, file: fileRef.current.files[0], titulo: programaTitulo },
      { onSuccess: () => { if (fileRef.current) fileRef.current.value = ''; setProgramaTitulo(''); } },
    );
  }

  function handleCrearEvaluacion() {
    if (!evForm.fecha) return;
    crearEvaluacion.mutate(evForm, {
      onSuccess: () => setEvForm((f) => ({ ...f, fecha: '', titulo: '' })),
    });
  }

  const handleToggle = useCallback((id: string) => {
    toggleEstado.mutate(id);
  }, [toggleEstado]);

  const isPending = crear.isPending || actualizar.isPending;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-body-sm text-on-surface-variant">
          {data?.total ?? 0} materia(s) registrada(s)
        </p>
        <Button type="button" variant="primary" icon="add" onClick={openCreate}>Nueva materia</Button>
      </div>

      <div className="relative">
        <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[18px] text-outline">search</span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar materias..."
          className="w-full rounded-lg border border-outline-variant bg-surface pl-9 pr-3 py-2 text-body-sm text-on-surface placeholder:text-outline focus:border-primary focus:outline-none"
        />
      </div>

      {isLoading ? (
        <LoadingState rows={4} cols={5} />
      ) : isError ? (
        <EmptyState message="Error al cargar materias" icon="error" />
      ) : materias.length === 0 ? (
        <EmptyState message={query ? 'No se encontraron materias' : 'No hay materias registradas'} icon="book" />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-outline-variant">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-outline-variant bg-surface-container-low">
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Código</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Carrera</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Cohorte</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-label-sm font-medium text-on-surface-variant">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {materias.map((m: Materia) => (
                <tr
                  key={m.id}
                  className={`border-b border-outline-variant transition-colors hover:bg-surface-container-low cursor-pointer ${
                    selectedMateria?.id === m.id ? 'bg-primary/5' : ''
                  }`}
                  onClick={() => handleSelectMateria(m)}
                >
                  <td className="px-4 py-3 text-body-sm font-medium text-on-surface">{m.nombre}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{m.codigo ?? '—'}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{m.carrera_nombre ?? '—'}</td>
                  <td className="px-4 py-3 text-body-sm text-on-surface-variant">{m.cohorte_nombre ?? '—'}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-0.5 text-label-xs font-medium ${
                        m.estado === 'Activo' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'
                      }`}
                    >
                      {m.estado}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); handleToggle(m.id); }}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                        title={m.estado === 'Activo' ? 'Desactivar' : 'Activar'}
                      >
                        <span className="material-symbols-outlined text-[18px]">
                          {m.estado === 'Activo' ? 'toggle_off' : 'toggle_on'}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); openEdit(m); }}
                        className="rounded-lg p-1.5 text-outline transition-colors hover:bg-surface-container-low hover:text-primary"
                        title="Editar"
                      >
                        <span className="material-symbols-outlined text-[18px]">edit</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedMateria && (
        <div className="rounded-xl border border-outline-variant bg-surface-container-low p-4 space-y-6">
          <div className="flex items-center justify-between">
            <h4 className="font-headline-md text-headline-md text-on-surface">
              {selectedMateria.nombre}
            </h4>
            <button
              type="button"
              onClick={() => setSelectedMateria(null)}
              className="rounded-lg p-1.5 text-outline hover:bg-surface-container"
            >
              <span className="material-symbols-outlined text-[18px]">close</span>
            </button>
          </div>

          <div className="space-y-3">
            <h5 className="text-label-sm font-medium text-on-surface-variant uppercase tracking-wide">Programa</h5>
            <div className="flex items-end gap-3">
              <div className="flex-1">
                <label className="mb-1 block text-label-sm text-on-surface-variant">Título</label>
                <input
                  type="text"
                  value={programaTitulo}
                  onChange={(e) => setProgramaTitulo(e.target.value)}
                  className="w-full rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                  placeholder="Ej: Programa 2024"
                />
              </div>
              <div className="flex-1">
                <label className="mb-1 block text-label-sm text-on-surface-variant">Archivo PDF</label>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf"
                  className="w-full text-body-sm text-on-surface file:mr-3 file:rounded-lg file:border-0 file:bg-primary/10 file:px-3 file:py-1.5 file:text-label-sm file:font-medium file:text-primary hover:file:bg-primary/20"
                />
              </div>
              <Button type="button" variant="primary" size="sm" icon="upload" onClick={handleSubirPrograma} disabled={subirPrograma.isPending || !fileRef.current?.files?.[0]}>
                {subirPrograma.isPending ? 'Subiendo…' : 'Subir'}
              </Button>
            </div>
            {subirPrograma.isSuccess && (
              <p className="text-label-sm text-success">Programa subido correctamente</p>
            )}
          </div>

          <div className="space-y-3">
            <h5 className="text-label-sm font-medium text-on-surface-variant uppercase tracking-wide">Evaluaciones</h5>
            {evaluaciones.length > 0 ? (
              <div className="overflow-x-auto rounded-lg border border-outline-variant">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-outline-variant bg-surface-container">
                      <th className="px-3 py-2 text-label-xs font-medium text-on-surface-variant">Tipo</th>
                      <th className="px-3 py-2 text-label-xs font-medium text-on-surface-variant">Instancia</th>
                      <th className="px-3 py-2 text-label-xs font-medium text-on-surface-variant">Título</th>
                      <th className="px-3 py-2 text-label-xs font-medium text-on-surface-variant">Fecha</th>
                    </tr>
                  </thead>
                  <tbody>
                    {evaluaciones.map((ev: Evaluacion) => (
                      <tr key={ev.id} className="border-b border-outline-variant">
                        <td className="px-3 py-2 text-body-sm text-on-surface capitalize">{ev.tipo}</td>
                        <td className="px-3 py-2 text-body-sm text-on-surface-variant">{ev.instancia}</td>
                        <td className="px-3 py-2 text-body-sm text-on-surface-variant">{ev.titulo ?? '—'}</td>
                        <td className="px-3 py-2 text-body-sm text-on-surface-variant">
                          {new Date(ev.fecha).toLocaleDateString('es-AR')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-body-sm text-on-surface-variant">No hay evaluaciones registradas</p>
            )}

            <div className="flex items-end gap-3 flex-wrap">
              <div>
                <label className="mb-1 block text-label-xs text-on-surface-variant">Tipo</label>
                <select
                  value={evForm.tipo}
                  onChange={(e) => setEvForm((f) => ({ ...f, tipo: e.target.value as CrearEvaluacionData['tipo'] }))}
                  className="rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                >
                  <option value="parcial">Parcial</option>
                  <option value="tp">TP</option>
                  <option value="coloquio">Coloquio</option>
                </select>
              </div>
              <div>
                <label className="mb-1 block text-label-xs text-on-surface-variant">Instancia</label>
                <input
                  type="number"
                  value={evForm.instancia}
                  onChange={(e) => setEvForm((f) => ({ ...f, instancia: Number(e.target.value) }))}
                  className="w-20 rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                  min={1}
                />
              </div>
              <div>
                <label className="mb-1 block text-label-xs text-on-surface-variant">Título</label>
                <input
                  type="text"
                  value={evForm.titulo}
                  onChange={(e) => setEvForm((f) => ({ ...f, titulo: e.target.value }))}
                  className="rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                  placeholder="Ej: Parcial 1"
                />
              </div>
              <div>
                <label className="mb-1 block text-label-xs text-on-surface-variant">Fecha</label>
                <input
                  type="date"
                  value={evForm.fecha}
                  onChange={(e) => setEvForm((f) => ({ ...f, fecha: e.target.value }))}
                  className="rounded-lg border border-outline-variant bg-surface px-3 py-2 text-body-sm text-on-surface focus:border-primary focus:outline-none"
                />
              </div>
              <Button type="button" variant="primary" size="sm" icon="add" onClick={handleCrearEvaluacion} disabled={crearEvaluacion.isPending || !evForm.fecha}>
                {crearEvaluacion.isPending ? 'Creando…' : 'Agregar'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setModalOpen(false)}>
          <div style={{ width: 400, maxWidth: '100%' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ background: 'var(--surface-container)', border: '1px solid var(--outline-variant)', borderRadius: 'var(--radius-lg)', padding: 28 }}>
              <h1 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
                {editTarget ? 'Editar materia' : 'Nueva materia'}
              </h1>
              <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>
                {editTarget ? 'Modificá los datos de la materia.' : 'Ingresá los datos de la nueva materia.'}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <Input
                  label="Nombre"
                  icon="menu_book"
                  placeholder="Ej: Álgebra"
                  value={form.nombre}
                  onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                />
                <Input
                  label="Código"
                  icon="tag"
                  placeholder="Ej: ALG-101"
                  value={form.codigo}
                  onChange={(e) => setForm((f) => ({ ...f, codigo: e.target.value }))}
                  helper="Opcional"
                />
                <Select
                  label="Carrera"
                  placeholder="Sin carrera"
                  value={form.carrera_id}
                  onChange={(e) => setForm((f) => ({ ...f, carrera_id: e.target.value }))}
                >
                  <option value="">Sin carrera</option>
                  {carreras.map((c) => (
                    <option key={c.id} value={c.id}>{c.nombre}</option>
                  ))}
                </Select>
                <Select
                  label="Cohorte"
                  placeholder="Sin cohorte"
                  value={form.cohorte_id}
                  onChange={(e) => setForm((f) => ({ ...f, cohorte_id: e.target.value }))}
                >
                  <option value="">Sin cohorte</option>
                  {cohortes.map((c) => (
                    <option key={c.id} value={c.id}>{c.nombre}</option>
                  ))}
                </Select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 28 }}>
                <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>Cancelar</Button>
                <Button type="button" variant="primary" onClick={handleSubmit} disabled={isPending || !form.nombre}>
                  {editTarget ? 'Guardar cambios' : 'Crear materia'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
