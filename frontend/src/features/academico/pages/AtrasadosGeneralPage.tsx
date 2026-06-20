/**
 * AtrasadosGeneralPage — Cross-materia atrasados view for PROFESORs.
 *
 * Uses GET /api/v1/profesor/atrasados (a single endpoint that returns all
 * the professor's atrasados across all materias), replacing the old approach
 * of fetching per-materia via /api/v1/materias/{id}/atrasados.
 *
 * Response: AtrasadoGeneral[] — each entry = one alumno in one dictado with
 * their pending activities list.
 *
 * TODO tutor: if TUTORs also need this page, add a tutor-specific endpoint.
 * For now this page is only visited by PROFESORs.
 */
import { useState } from 'react';
import { useAtrasadosGeneralProfesor } from '@/features/profesor/hooks/useProfesor';
import type { AtrasadoGeneral } from '@/features/profesor/types';

export function AtrasadosGeneralPage() {
  const { data, isLoading } = useAtrasadosGeneralProfesor();
  const [filtroMateria, setFiltroMateria] = useState<string>('');

  // Derive unique materias for the filter dropdown
  const materias = Array.from(
    new Map((data ?? []).map((e) => [e.materia_nombre, e.materia_nombre])).values(),
  ).sort();

  const filtered = filtroMateria
    ? (data ?? []).filter((e) => e.materia_nombre === filtroMateria)
    : (data ?? []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          Alumnos Atrasados
        </h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>
          Vista consolidada de todos tus alumnos con actividades pendientes
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
          {materias.length > 1 && (
            <div>
              <label
                htmlFor="filtro-materia"
                style={{ fontSize: 13, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 6 }}
              >
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
                {materias.map((m) => (
                  <option key={m} value={m}>{m}</option>
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
              <span
                className="material-symbols-outlined"
                style={{ fontSize: 48, display: 'block', marginBottom: 12, color: 'var(--primary)' }}
              >
                check_circle
              </span>
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
                    {['Alumno', 'Materia', 'Actividades pendientes'].map((h) => (
                      <th
                        key={h}
                        style={{
                          padding: '10px 16px',
                          textAlign: 'left',
                          fontSize: 12,
                          fontWeight: 600,
                          color: 'var(--on-surface-variant)',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((row: AtrasadoGeneral, i) => (
                    <tr
                      key={`${row.entrada_padron_id}-${i}`}
                      style={{ borderBottom: '1px solid var(--outline-variant)' }}
                    >
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface)' }}>
                        <div style={{ fontWeight: 600 }}>
                          {row.apellido}, {row.nombre}
                        </div>
                      </td>
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface-variant)' }}>
                        {row.materia_nombre}
                      </td>
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface)' }}>
                        {row.actividades_sin_entrega.length === 0 ? (
                          <span style={{ color: 'var(--on-surface-variant)' }}>—</span>
                        ) : (
                          <ul style={{ margin: 0, paddingLeft: 16 }}>
                            {row.actividades_sin_entrega.map((act, j) => (
                              <li key={j} style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>
                                {act}
                              </li>
                            ))}
                          </ul>
                        )}
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
