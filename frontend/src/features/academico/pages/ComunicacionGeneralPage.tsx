import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import * as api from '@/shared/services/api';
import type { Materia } from '../types';

function useMisMaterias() {
  return useQuery<Materia[]>({
    queryKey: ['academico', 'mis-materias'],
    queryFn: () => api.get<Materia[]>('/api/v1/materias/mis-materias'),
  });
}

export function ComunicacionGeneralPage() {
  const navigate = useNavigate();
  const { data: materias, isLoading } = useMisMaterias();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          Comunicación
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Seleccioná una materia para enviar comunicaciones a tus alumnos atrasados
        </p>
      </div>

      {isLoading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 24, color: 'var(--on-surface-variant)' }}>
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-outline-variant border-t-primary" role="status" />
          Cargando materias…
        </div>
      )}

      {!isLoading && (!materias || materias.length === 0) && (
        <div
          data-testid="empty-state"
          style={{
            padding: 48,
            textAlign: 'center',
            color: 'var(--on-surface-variant)',
            background: 'var(--surface-container)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--outline-variant)',
          }}
        >
          <span className="material-symbols-outlined" style={{ fontSize: 48, display: 'block', marginBottom: 12, color: 'var(--on-surface-variant)' }}>send</span>
          <p style={{ margin: '0 0 4px', fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
            Sin materias asignadas
          </p>
          <p style={{ margin: 0, fontSize: 14, color: 'var(--on-surface-variant)' }}>
            No tenés materias asignadas para el período activo.
          </p>
        </div>
      )}

      {!isLoading && materias && materias.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {materias.map((materia) => (
            <div
              key={materia.id}
              data-testid={`materia-row-${materia.id}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '16px 20px',
                background: 'var(--surface-container)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--outline-variant)',
                gap: 16,
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--on-surface)', marginBottom: 2 }}>
                  {materia.nombre}
                </div>
                <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>
                  {materia.codigo} · {materia.carrera} · Comisión {materia.comision}
                </div>
              </div>

              <button
                data-testid={`comunicar-btn-${materia.id}`}
                onClick={() => navigate(`/materias/${materia.id}/comunicar`)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '8px 16px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--primary)',
                  background: 'transparent',
                  color: 'var(--primary)',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                <span className="material-symbols-outlined" style={{ fontSize: 16 }}>send</span>
                Comunicar
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
