import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Tabs, Badge, Button } from '@/shared/components/ds';
import * as alumnoService from '../services/alumno.service';
import type { AvisoAlumno } from '../types/alumno.types';

type FiltroLeido = 'todos' | 'no_leidos' | 'leidos';

const severidadTone: Record<string, 'danger' | 'warning' | 'neutral'> = {
  ERROR: 'danger',
  ADVERTENCIA: 'warning',
  INFO: 'neutral',
};

const severidadLabel: Record<string, string> = {
  ERROR: 'Alta',
  ADVERTENCIA: 'Media',
  INFO: 'Baja',
};

const TABS = [
  { id: 'todos', label: 'Todos' },
  { id: 'no_leidos', label: 'No leídos' },
  { id: 'leidos', label: 'Leídos' },
];

export function MisAvisosPage() {
  const queryClient = useQueryClient();
  const [filtro, setFiltro] = useState<FiltroLeido>('todos');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'avisos'],
    queryFn: () => alumnoService.getAvisos(),
  });

  const confirmarMutation = useMutation({
    mutationFn: (avisoId: string) => alumnoService.confirmarAviso(avisoId),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['alumno', 'avisos'] }); },
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar avisos"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader />
        <EmptyState icon="campaign" title="No hay avisos activos" />
      </div>
    );
  }

  const filtrados = data.filter((a: AvisoAlumno) => {
    if (filtro === 'no_leidos') return !a.acknowledged;
    if (filtro === 'leidos') return a.acknowledged;
    return true;
  });

  const unread = data.filter((a) => !a.acknowledged).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader />

      <Tabs
        tabs={TABS.map((t) => ({ ...t, badge: t.id === 'no_leidos' && unread > 0 ? unread : undefined }))}
        value={filtro}
        onChange={(id) => setFiltro(id as FiltroLeido)}
      />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {filtrados.length === 0 ? (
          <EmptyState icon="filter_alt" title="Sin resultados" message="No hay avisos que coincidan con el filtro." />
        ) : (
          filtrados.map((aviso: AvisoAlumno) => (
            <div
              key={aviso.id}
              style={{
                background: 'var(--surface-container-lowest)',
                borderRadius: 'var(--radius-lg)',
                border: `1px solid ${!aviso.acknowledged ? 'color-mix(in srgb, var(--primary) 30%, transparent)' : 'var(--outline-variant)'}`,
                padding: 16,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    {!aviso.acknowledged && (
                      <span style={{ width: 8, height: 8, borderRadius: 'var(--radius-full)', background: 'var(--primary)', flexShrink: 0 }} />
                    )}
                    <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--on-surface)' }}>{aviso.titulo}</span>
                    <Badge tone={severidadTone[aviso.severidad] ?? 'neutral'}>
                      {severidadLabel[aviso.severidad] ?? aviso.severidad}
                    </Badge>
                  </div>
                  <p style={{ margin: '0 0 8px', fontSize: 14, color: 'var(--on-surface-variant)', lineHeight: 1.5, whiteSpace: 'pre-line' }}>{aviso.cuerpo}</p>
                  <div style={{ fontSize: 12, color: 'var(--outline)', fontFamily: 'var(--font-mono)' }}>
                    {new Date(aviso.fecha_publicacion).toLocaleDateString('es-AR', { day: 'numeric', month: 'long', year: 'numeric' })}
                    {aviso.vigencia_hasta && ` · Válido hasta ${new Date(aviso.vigencia_hasta).toLocaleDateString('es-AR')}`}
                  </div>
                </div>

                {aviso.requiere_ack && !aviso.acknowledged && (
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => confirmarMutation.mutate(aviso.id)}
                    disabled={confirmarMutation.isPending}
                  >
                    {confirmarMutation.isPending ? 'Confirmando…' : 'Confirmar lectura'}
                  </Button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function PageHeader() {
  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Avisos</h2>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Tablón de avisos y comunicaciones oficiales</p>
    </div>
  );
}
