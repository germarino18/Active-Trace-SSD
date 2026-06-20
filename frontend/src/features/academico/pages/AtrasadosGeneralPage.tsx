/**
 * AtrasadosGeneralPage — Cross-materia desaprobados/atrasados view for PROFESORs.
 *
 * Uses GET /api/v1/profesor/atrasados (one endpoint returning all the
 * professor's atrasados across materias). Response: AtrasadoGeneral[].
 *
 * D7: Groups rows by alumno (entrada_padron_id); distinct materias comma-
 * separated. Per-row "Comunicado individual" + top-level "Enviar a todos"
 * open ComunicadoFlexibleForm (actividad optional).
 */
import { useState } from 'react';
import { useAtrasadosGeneralProfesor } from '@/features/profesor/hooks/useProfesor';
import { Button } from '@/shared/components/ds';
import { ComunicadoFlexibleForm } from '../components/ComunicadoFlexibleForm';
import type { AtrasadoGeneral, ComunicadoDestinatario } from '@/features/profesor/types';

interface AlumnoAgrupado {
  entrada_padron_id: string;
  nombre: string;
  apellido: string;
  materias: string;
  _materiasArr: string[];
}

function groupByAlumno(rows: AtrasadoGeneral[]): AlumnoAgrupado[] {
  const map = new Map<string, AlumnoAgrupado>();
  for (const row of rows) {
    const existing = map.get(row.entrada_padron_id);
    if (existing) {
      if (!existing._materiasArr.includes(row.materia_nombre)) {
        existing._materiasArr.push(row.materia_nombre);
        existing.materias = existing._materiasArr.join(', ');
      }
    } else {
      map.set(row.entrada_padron_id, {
        entrada_padron_id: row.entrada_padron_id,
        nombre: row.nombre,
        apellido: row.apellido,
        materias: row.materia_nombre,
        _materiasArr: [row.materia_nombre],
      });
    }
  }
  return Array.from(map.values());
}

/** Build a deduped destinatarios set ({entrada_padron_id, dictado_id}) from raw rows. */
function buildDestinatarios(rows: AtrasadoGeneral[], epId?: string): ComunicadoDestinatario[] {
  const seen = new Set<string>();
  const out: ComunicadoDestinatario[] = [];
  for (const r of rows) {
    if (epId && r.entrada_padron_id !== epId) continue;
    const key = `${r.entrada_padron_id}:${r.dictado_id}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({ entrada_padron_id: r.entrada_padron_id, dictado_id: r.dictado_id });
  }
  return out;
}

interface ComunicadoState {
  titulo: string;
  destinatarios: ComunicadoDestinatario[];
  materias?: string;
}

export function AtrasadosGeneralPage() {
  const { data, isLoading } = useAtrasadosGeneralProfesor();
  const [filtroMateria, setFiltroMateria] = useState<string>('');
  const [comunicado, setComunicado] = useState<ComunicadoState | null>(null);

  const materias = Array.from(
    new Map((data ?? []).map((e) => [e.materia_nombre, e.materia_nombre])).values(),
  ).sort();

  const filteredRaw = filtroMateria
    ? (data ?? []).filter((e) => e.materia_nombre === filtroMateria)
    : (data ?? []);

  const grouped = groupByAlumno(filteredRaw);

  const openIndividual = (row: AlumnoAgrupado) =>
    setComunicado({
      titulo: `Comunicado para ${row.apellido}, ${row.nombre}`,
      destinatarios: buildDestinatarios(filteredRaw, row.entrada_padron_id),
      materias: row.materias,
    });

  const openGeneral = () =>
    setComunicado({
      titulo: 'Comunicado general a desaprobados/atrasados',
      destinatarios: buildDestinatarios(filteredRaw),
    });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
          Desaprobados/Atrasados
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

      {!isLoading && comunicado && (
        <ComunicadoFlexibleForm
          titulo={comunicado.titulo}
          destinatarios={comunicado.destinatarios}
          materias={comunicado.materias}
          onClose={() => setComunicado(null)}
        />
      )}

      {!isLoading && !comunicado && (
        <>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
            {materias.length > 1 ? (
              <div>
                <label htmlFor="filtro-materia" style={{ fontSize: 13, color: 'var(--on-surface-variant)', display: 'block', marginBottom: 6 }}>
                  Filtrar por materia
                </label>
                <select
                  id="filtro-materia"
                  value={filtroMateria}
                  onChange={(e) => setFiltroMateria(e.target.value)}
                  style={{ padding: '8px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--outline-variant)', background: 'var(--surface-container)', color: 'var(--on-surface)', fontSize: 14, minWidth: 240 }}
                >
                  <option value="">Todas las materias</option>
                  {materias.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            ) : <span />}
            {grouped.length > 0 && (
              <Button variant="primary" size="sm" onClick={openGeneral}>
                <span className="material-symbols-outlined text-[16px]">campaign</span>
                Enviar a todos
              </Button>
            )}
          </div>

          {grouped.length === 0 ? (
            <div
              data-testid="empty-state"
              style={{ padding: 48, textAlign: 'center', color: 'var(--on-surface-variant)', background: 'var(--surface-container)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)' }}
            >
              <span className="material-symbols-outlined" style={{ fontSize: 48, display: 'block', marginBottom: 12, color: 'var(--primary)' }}>
                check_circle
              </span>
              <p style={{ margin: 0, fontSize: 16, fontWeight: 600, color: 'var(--on-surface)' }}>
                No hay alumnos atrasados en ninguna de tus materias
              </p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table data-testid="atrasados-table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--outline-variant)' }}>
                    {['Alumno', 'Materias', ''].map((h, i) => (
                      <th key={h || `col-${i}`} style={{ padding: '10px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--on-surface-variant)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {grouped.map((row: AlumnoAgrupado) => (
                    <tr key={row.entrada_padron_id} style={{ borderBottom: '1px solid var(--outline-variant)' }}>
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface)' }}>
                        <div style={{ fontWeight: 600 }}>{row.apellido}, {row.nombre}</div>
                      </td>
                      <td style={{ padding: '12px 16px', color: 'var(--on-surface-variant)' }}>{row.materias}</td>
                      <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                        <Button variant="secondary" size="sm" onClick={() => openIndividual(row)}>
                          <span className="material-symbols-outlined text-[14px]">send</span>
                          Comunicado individual
                        </Button>
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
