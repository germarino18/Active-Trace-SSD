import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Select, Badge, Button } from '@/shared/components/ds';
import * as alumnoService from '../services/alumno.service';

export function MisFechasPage() {
  const [filtroMateria, setFiltroMateria] = useState<string>('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'fechas'],
    queryFn: () => alumnoService.getFechas(),
  });

  const materias = useMemo(() => {
    if (!data) return [];
    return [...new Set(data.map((f) => f.materia_nombre))];
  }, [data]);

  const filtradas = useMemo(() => {
    if (!data) return [];
    if (!filtroMateria) return data;
    return data.filter((f) => f.materia_nombre === filtroMateria);
  }, [data, filtroMateria]);

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar fechas"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader />
        <EmptyState icon="calendar_month" title="No hay fechas académicas registradas" />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader />

      <Select
        label="Filtrar por materia"
        value={filtroMateria}
        onChange={(e) => setFiltroMateria(e.target.value)}
        options={[
          { value: '', label: 'Todas las materias' },
          ...materias.map((m) => ({ value: m, label: m })),
        ]}
        style={{ maxWidth: 320 }}
      />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {filtradas.length === 0 ? (
          <EmptyState icon="filter_alt" title="Sin resultados" message="No hay fechas para el filtro seleccionado." />
        ) : (
          filtradas.map((fecha) => {
            const d = new Date(fecha.fecha);
            return (
              <div
                key={fecha.id}
                style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--surface-container-lowest)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)', padding: 16 }}
              >
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: 56, height: 56, borderRadius: 'var(--radius-md)', background: 'color-mix(in srgb, var(--primary) 12%, transparent)', flexShrink: 0 }}>
                  <span style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', color: 'var(--primary)' }}>
                    {d.toLocaleDateString('es-AR', { month: 'short' })}
                  </span>
                  <span style={{ fontSize: 24, fontWeight: 700, color: 'var(--primary)', lineHeight: 1 }}>
                    {d.getDate()}
                  </span>
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--on-surface)' }}>{fecha.descripcion}</div>
                  <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', marginTop: 2 }}>{fecha.materia_nombre}</div>
                  <div style={{ marginTop: 6 }}>
                    <Badge tone="neutral">{fecha.tipo}</Badge>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

function PageHeader() {
  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Calendario Académico</h2>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Fechas importantes de tus materias</p>
    </div>
  );
}
