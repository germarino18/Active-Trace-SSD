import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useModificarVigencia } from '../hooks/useEquipos';
import { HelpButton } from '../components/HelpButton';
import { EmptyState } from '@/features/academico/components/EmptyState';

export function ModificarVigenciaPage() {
  const { hasAnyPermission } = useAuth();
  const navigate = useNavigate();
  const vigenciaMutation = useModificarVigencia();

  const [materiaId, setMateriaId] = useState('');
  const [carreraId, setCarreraId] = useState('');
  const [cohorteId, setCohorteId] = useState('');
  const [vigenciaHasta, setVigenciaHasta] = useState('');

  if (!hasAnyPermission(['COORDINADOR', 'ADMIN'])) {
    return <EmptyState message="No tenés permisos para modificar vigencias" icon="lock" />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await vigenciaMutation.mutateAsync({
        materia_id: materiaId,
        carrera_id: carreraId,
        cohorte_id: cohorteId,
        vigencia_hasta: vigenciaHasta,
      });
      navigate('/coordinacion/equipos');
    } catch {
      // Error handled by mutation
    }
  };

  const fieldClass = 'w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary';
  const labelClass = 'text-label-xs font-medium text-outline uppercase tracking-wider';

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div className="flex items-center gap-2">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Modificar Vigencia</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Extendé la fecha de vigencia de todas las asignaciones de un equipo
          </p>
        </div>
        <HelpButton tooltip="Seleccioná un equipo (materia × carrera × cohorte) y establecé una nueva fecha de fin para todas sus asignaciones activas." />
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md space-y-5">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-1">
              <label className={labelClass}>Materia</label>
              <input
                value={materiaId}
                onChange={(e) => setMateriaId(e.target.value)}
                placeholder="ID de materia"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Carrera</label>
              <input
                value={carreraId}
                onChange={(e) => setCarreraId(e.target.value)}
                placeholder="ID de carrera"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Cohorte</label>
              <input
                value={cohorteId}
                onChange={(e) => setCohorteId(e.target.value)}
                placeholder="Ej: 2024"
                className={fieldClass}
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className={labelClass}>Nueva fecha de fin</label>
            <input
              type="date"
              value={vigenciaHasta}
              onChange={(e) => setVigenciaHasta(e.target.value)}
              className={fieldClass}
              required
            />
            <p className="text-label-xs text-on-surface-variant mt-1">
              Todas las asignaciones activas de este equipo se actualizarán a esta fecha
            </p>
          </div>
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
            disabled={vigenciaMutation.isPending}
            className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {vigenciaMutation.isPending ? 'Guardando...' : 'Actualizar vigencia'}
          </button>
        </div>
      </form>
    </div>
  );
}
