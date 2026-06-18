import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useClonarEquipo } from '../hooks/useEquipos';
import { HelpButton } from '../components/HelpButton';
import { EmptyState } from '@/features/academico/components/EmptyState';

export function ClonarEquipoPage() {
  const { hasAnyPermission } = useAuth();
  const navigate = useNavigate();
  const clonarMutation = useClonarEquipo();

  const [origenMateria, setOrigenMateria] = useState('');
  const [origenCarrera, setOrigenCarrera] = useState('');
  const [origenCohorte, setOrigenCohorte] = useState('');
  const [destinoMateria, setDestinoMateria] = useState('');
  const [destinoCarrera, setDestinoCarrera] = useState('');
  const [destinoCohorte, setDestinoCohorte] = useState('');
  const [successModal, setSuccessModal] = useState<{ clonadas: number } | null>(null);

  if (!hasAnyPermission(['COORDINADOR', 'ADMIN'])) {
    return <EmptyState message="No tenés permisos para clonar equipos" icon="lock" />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await clonarMutation.mutateAsync({
        origen_materia_id: origenMateria,
        origen_carrera_id: origenCarrera,
        origen_cohorte_id: origenCohorte,
        destino_materia_id: destinoMateria,
        destino_carrera_id: destinoCarrera,
        destino_cohorte_id: destinoCohorte,
      });
      setSuccessModal({ clonadas: result.clonadas });
    } catch {
      // Error handled by mutation
    }
  };

  const fieldClass = 'w-full rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary';
  const labelClass = 'text-label-xs font-medium text-outline uppercase tracking-wider';
  const sectionClass = 'rounded-xl border border-outline-variant bg-surface-container-lowest p-md space-y-4';

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-2">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Clonar Equipo Docente</h2>
          <p className="text-body-md text-on-surface-variant mt-1">
            Copiá todas las asignaciones de un equipo origen a un destino
          </p>
        </div>
        <HelpButton tooltip="Cloná la configuración completa de un equipo docente (materia × carrera × cohorte) a otra combinación. Todas las asignaciones se replican con el mismo rol." />
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div className={sectionClass}>
          <h3 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px] text-primary">source</span>
            Equipo origen
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-1">
              <label className={labelClass}>Materia</label>
              <input
                value={origenMateria}
                onChange={(e) => setOrigenMateria(e.target.value)}
                placeholder="ID de materia"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Carrera</label>
              <input
                value={origenCarrera}
                onChange={(e) => setOrigenCarrera(e.target.value)}
                placeholder="ID de carrera"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Cohorte</label>
              <input
                value={origenCohorte}
                onChange={(e) => setOrigenCohorte(e.target.value)}
                placeholder="Ej: 2024"
                className={fieldClass}
                required
              />
            </div>
          </div>
        </div>

        <div className="flex justify-center">
          <span className="material-symbols-outlined text-[32px] text-outline">arrow_downward</span>
        </div>

        <div className={sectionClass}>
          <h3 className="font-headline-md text-headline-md text-on-surface flex items-center gap-2">
            <span className="material-symbols-outlined text-[20px] text-primary">destination</span>
            Equipo destino
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-1">
              <label className={labelClass}>Materia</label>
              <input
                value={destinoMateria}
                onChange={(e) => setDestinoMateria(e.target.value)}
                placeholder="ID de materia"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Carrera</label>
              <input
                value={destinoCarrera}
                onChange={(e) => setDestinoCarrera(e.target.value)}
                placeholder="ID de carrera"
                className={fieldClass}
                required
              />
            </div>
            <div className="space-y-1">
              <label className={labelClass}>Cohorte</label>
              <input
                value={destinoCohorte}
                onChange={(e) => setDestinoCohorte(e.target.value)}
                placeholder="Ej: 2025"
                className={fieldClass}
                required
              />
            </div>
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
            disabled={clonarMutation.isPending}
            className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {clonarMutation.isPending ? 'Clonando...' : 'Clonar equipo'}
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
            <span className="material-symbols-outlined text-[48px] text-success">content_copy</span>
            <h3 className="mt-3 font-headline-lg text-headline-lg text-on-surface">
              Equipo clonado
            </h3>
            <p className="mt-2 text-body-md text-on-surface-variant">
              {successModal.clonadas > 0
                ? `${successModal.clonadas} asignaciones copiadas al equipo destino`
                : 'No se clonaron asignaciones. El equipo origen puede estar vacío.'}
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
