import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useDocentes, useAsignacionMasiva } from '../hooks/useEquipos';
import { HelpButton } from '../components/HelpButton';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '@/features/academico/components/EmptyState';
import type { Docente } from '../types';

export function AsignacionMasivaPage() {
  const { hasAnyPermission } = useAuth();
  const navigate = useNavigate();
  const { data: docentes, isLoading: docentesLoading } = useDocentes();
  const masivaMutation = useAsignacionMasiva();

  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [materiaId, setMateriaId] = useState('');
  const [carreraId, setCarreraId] = useState('');
  const [cohorteId, setCohorteId] = useState('');
  const [rol, setRol] = useState('');
  const [vigenciaDesde, setVigenciaDesde] = useState('');
  const [vigenciaHasta, setVigenciaHasta] = useState('');
  const [successModal, setSuccessModal] = useState<{ creadas: number } | null>(null);

  if (!hasAnyPermission(['COORDINADOR', 'ADMIN'])) {
    return <EmptyState message="No tenés permisos para asignaciones masivas" icon="lock" />;
  }

  const toggleDocente = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const toggleAll = () => {
    if (!docentes) return;
    if (selectedIds.size === docentes.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(docentes.map((d) => d.id)));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedIds.size === 0) return;

    try {
      const result = await masivaMutation.mutateAsync({
        usuario_ids: Array.from(selectedIds),
        materia_id: materiaId,
        carrera_id: carreraId,
        cohorte_id: cohorteId,
        rol,
        vigencia_desde: vigenciaDesde,
        vigencia_hasta: vigenciaHasta,
      });
      setSuccessModal({ creadas: result.creadas });
    } catch {
      // Error handled by mutation
    }
  };

  const fieldClass = 'w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary';
  const labelClass = 'text-label-xs font-medium text-outline uppercase tracking-wider';

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-2">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Asignación Masiva</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Asigná múltiples docentes a una misma materia en una sola operación
          </p>
        </div>
        <HelpButton tooltip="Seleccioná varios docentes de la lista y asignalos todos a la misma materia, carrera, cohorte y rol con las mismas fechas de vigencia." />
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className={labelClass}>Materia</label>
              <input
                value={materiaId}
                onChange={(e) => setMateriaId(e.target.value)}
                placeholder="ID de la materia"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Rol</label>
              <select value={rol} onChange={(e) => setRol(e.target.value)} className={fieldClass} required>
                <option value="">Seleccionar rol...</option>
                <option value="PROFESOR">Profesor</option>
                <option value="TUTOR">Tutor</option>
                <option value="NEXO">Nexo</option>
                <option value="COORDINADOR">Coordinador</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className={labelClass}>Carrera</label>
              <input
                value={carreraId}
                onChange={(e) => setCarreraId(e.target.value)}
                placeholder="ID de la carrera"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Cohorte</label>
              <input
                value={cohorteId}
                onChange={(e) => setCohorteId(e.target.value)}
                placeholder="ID de la cohorte"
                className={fieldClass}
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className={labelClass}>Vigencia desde</label>
              <input
                type="date"
                value={vigenciaDesde}
                onChange={(e) => setVigenciaDesde(e.target.value)}
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Vigencia hasta</label>
              <input
                type="date"
                value={vigenciaHasta}
                onChange={(e) => setVigenciaHasta(e.target.value)}
                className={fieldClass}
                required
              />
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md space-y-3">
          <div className="flex items-center justify-between">
            <label className={labelClass}>Docentes ({selectedIds.size} seleccionados)</label>
            <button
              type="button"
              onClick={toggleAll}
              className="text-label-xs text-primary hover:underline"
            >
              {selectedIds.size === (docentes?.length ?? 0)
                ? 'Deseleccionar todos'
                : 'Seleccionar todos'}
            </button>
          </div>

          {docentesLoading ? (
            <div className="flex justify-center py-4">
              <Spinner size="sm" />
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {docentes?.map((docente: Docente) => (
                <label
                  key={docente.id}
                  className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 transition-colors ${
                    selectedIds.has(docente.id)
                      ? 'border-primary bg-primary/5'
                      : 'border-outline-variant hover:bg-surface-container-low'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedIds.has(docente.id)}
                    onChange={() => toggleDocente(docente.id)}
                    className="h-4 w-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary"
                  />
                  <div className="min-w-0 flex-1">
                    <p className="text-label-sm text-on-surface truncate">
                      {docente.apellido}, {docente.nombre}
                    </p>
                    <p className="text-label-xs text-on-surface-variant truncate">{docente.email}</p>
                  </div>
                </label>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={() => navigate('/coordinacion/equipos')}
            className="rounded-lg border border-outline-variant px-4 py-2 text-label-sm font-medium text-on-surface transition-colors hover:bg-surface-container-low"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={masivaMutation.isPending || selectedIds.size === 0}
            className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {masivaMutation.isPending
              ? 'Asignando...'
              : `Asignar (${selectedIds.size} docentes)`}
          </button>
        </div>
      </form>

      {successModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
          onClick={() => setSuccessModal(null)}
        >
          <div
            className="mx-4 w-full max-w-sm rounded-xl border border-outline-variant bg-surface p-6 shadow-xl text-center"
            onClick={(e) => e.stopPropagation()}
          >
            <span className="material-symbols-outlined text-[48px] text-success">check_circle</span>
            <h3 className="mt-3 font-headline-lg text-headline-lg text-on-surface">
              Asignación completada
            </h3>
            <p className="mt-2 text-body-md text-on-surface-variant">
              {successModal.creadas} asignaciones creadas correctamente
            </p>
            <button
              type="button"
              onClick={() => {
                setSuccessModal(null);
                navigate('/coordinacion/equipos');
              }}
              className="mt-5 rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90"
            >
              Ir a equipos
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
