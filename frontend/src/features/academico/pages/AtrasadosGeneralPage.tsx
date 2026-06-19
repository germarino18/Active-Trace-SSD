import { useState } from 'react';
import { useQuery, useQueries } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import * as api from '@/shared/services/api';
import type { Materia, AtrasadosResponse, AtrasadoEntry } from '../types';

function useMisMaterias() {
  return useQuery<Materia[]>({
    queryKey: ['academico', 'mis-materias'],
    queryFn: () => api.get<Materia[]>('/api/v1/materias/mis-materias'),
  });
}

interface FlatAtrasado extends AtrasadoEntry {
  materiaId: string;
  materiaNombre: string;
}

export function AtrasadosGeneralPage() {
  const navigate = useNavigate();
  const [filtroMateria, setFiltroMateria] = useState<string>('');
  const { data: materias, isLoading: loadingMaterias } = useMisMaterias();

  const atrasadosQueries = useQueries({
    queries: (materias ?? []).map((m) => ({
      queryKey: ['atrasados', m.id],
      queryFn: () => api.get<AtrasadosResponse>(`/api/v1/materias/${m.id}/atrasados`),
      enabled: !!materias,
    })),
  });

  const isLoading = loadingMaterias || atrasadosQueries.some((q) => q.isLoading);

  const flatAtrasados: FlatAtrasado[] = (materias ?? []).flatMap((materia, idx) => {
    const result = atrasadosQueries[idx]?.data;
    if (!result) return [];
    return result.alumnos
      .filter((a) => a.estado === 'atrasado')
      .map((entry) => ({
        ...entry,
        materiaId: materia.id,
        materiaNombre: materia.nombre,
      }));
  });

  const filtered = filtroMateria
    ? flatAtrasados.filter((a) => a.materiaId === filtroMateria)
    : flatAtrasados;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          Alumnos Atrasados
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Vista consolidada de todos tus alumnos atrasados
        </p>
      </div>

      {isLoading && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 24, color: 'var(--on-surface-variant)' }}>
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-outline-variant border-t-primary" role="status" />
          Cargando atrasados…
        </div>
      )}

      {!isLoading && (
        <>
          {(materias ?? []).length > 1 && (
            <div>
              <label htmlFor="filtro-materia" style={{ fontSize: 13, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 6 }}>
                Filtrar por materia
              </label>
              <select
                id="filtro-materia"
                value={filtroMateria}
                onChange={(e) => setFiltroMateria(e.target.value)}
                style={{
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--outline-variant)',
                  background: 'var(--surface-container)',
                  color: 'var(--on-surface)',
                  fontSize: 14,
                  minWidth: 240,
                }}
              >
                <option value="">Todas las materias</option>
                {(materias ?? []).map((m) => (
                  <option key={m.id} value={m.id}>{m.nombre}</option>
                ))}
              </select>
            </div>
          )}

          {filtered.length === 0 ? (
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
              <span className="material-symbols-outlined" style={{ fontSize: 48, display: 'block', marginBottom: 12, color: 'var(--primary)' }}>check_circle</span>
              <p style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
                No hay alumnos atrasados en ninguna de tus materias
              </p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table
                data-testid="atrasados-table"
                style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}
              >
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--outline-variant)' }}>
                    {['Alumno', 'Materia', 'Act. pendientes', '% Aprobación', 'Estado'].map((h) => (
                      <th
                        key={h}
                        style={{ padding: '10px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--on-surface-variant)', textTransform: 'uppercase', letterSpacing: '0.05em' }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((row, i) => (
                    <tr
                      key={`${row.materiaId}-${row.alumno.id}-${i}`}
                      style={{ borderBottom: '1px solid var(--outline-variant)', cursor: 'pointer' }}
                      onClick={() => navigate(`/materias/${row.materiaId}/atrasados`)}
                    >
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface)' }}>
                        <div style={{ fontWeight: 600 }}>{row.alumno.apellido}, {row.alumno.nombre}</div>
                        <div style={{ fontSize: 12, color: 'var(--on-surface-variant)' }}>{row.alumno.email}</div>
                      </td>
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface-variant)' }}>{row.materiaNombre}</td>
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface)' }}>{row.actividades_pendientes}</td>
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface)' }}>{row.porcentaje.toFixed(1)}%</td>
                      <td style={{ padding: '12px 16px' }}>
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: 999,
                          fontSize: 12,
                          fontWeight: 600,
                          background: 'color-mix(in srgb, var(--error) 16%, transparent)',
                          color: 'var(--error)',
                        }}>
                          Atrasado
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
