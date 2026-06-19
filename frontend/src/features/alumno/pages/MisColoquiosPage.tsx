import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Badge, Button } from '@/shared/components/ds';
import { ReservaTurnoModal } from '../components/ReservaTurnoModal';
import * as alumnoService from '../services/alumno.service';
import type { ConvocatoriaColoquio } from '../types/alumno.types';

export function MisColoquiosPage() {
  const [selectedConvocatoria, setSelectedConvocatoria] = useState<ConvocatoriaColoquio | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'coloquios'],
    queryFn: () => alumnoService.getConvocatorias(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar convocatorias"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader />
        <EmptyState icon="quiz" title="No hay convocatorias de coloquio abiertas" />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {data.map((convocatoria) => {
          const totalCupos = convocatoria.fechas.reduce((acc, f) => acc + f.cupos_restantes, 0);

          return (
            <div
              key={convocatoria.id}
              style={{ background: 'var(--surface-container-lowest)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--outline-variant)', padding: 20 }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12, gap: 16, flexWrap: 'wrap' }}>
                <div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--on-surface)' }}>{convocatoria.materia_nombre}</div>
                  <div style={{ fontSize: 13, color: 'var(--on-surface-variant)', marginTop: 2 }}>
                    {convocatoria.fechas.length} fecha{convocatoria.fechas.length !== 1 ? 's' : ''} disponible{convocatoria.fechas.length !== 1 ? 's' : ''} · {totalCupos > 0 ? `${totalCupos} cupo${totalCupos !== 1 ? 's' : ''}` : 'Sin cupos'}
                  </div>
                </div>
                <div style={{ fontSize: 12, color: 'var(--on-surface-variant)', fontFamily: 'var(--font-mono)' }}>
                  Límite: {new Date(convocatoria.fecha_limite).toLocaleDateString('es-AR')}
                </div>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
                {convocatoria.fechas.map((f) => (
                  <Badge key={f.fecha_id} tone={f.cupos_restantes > 0 ? 'success' : 'danger'}>
                    {new Date(f.fecha).toLocaleDateString('es-AR')} · {f.cupos_restantes} cupo{f.cupos_restantes !== 1 ? 's' : ''}
                  </Badge>
                ))}
              </div>

              <Button
                variant="primary"
                size="sm"
                icon="event_seat"
                disabled={totalCupos === 0}
                onClick={() => setSelectedConvocatoria(convocatoria)}
              >
                Reservar turno
              </Button>
            </div>
          );
        })}
      </div>

      {selectedConvocatoria && (
        <ReservaTurnoModal
          convocatoria={selectedConvocatoria}
          onClose={() => setSelectedConvocatoria(null)}
        />
      )}
    </div>
  );
}

function PageHeader() {
  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Coloquios</h2>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Reservá tu turno para los coloquios disponibles</p>
    </div>
  );
}
