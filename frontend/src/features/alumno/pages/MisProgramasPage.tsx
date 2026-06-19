import { useQuery } from '@tanstack/react-query';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Card, Button } from '@/shared/components/ds';
import * as alumnoService from '../services/alumno.service';

export function MisProgramasPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['alumno', 'programas'],
    queryFn: () => alumnoService.getProgramas(),
  });

  if (isLoading) return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar programas"
        action={<Button variant="secondary" icon="refresh" onClick={() => refetch()}>Reintentar</Button>}
      />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
        <PageHeader />
        <EmptyState icon="description" title="No hay programas disponibles" />
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <PageHeader />

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 }}>
        {data.map((programa) => (
          <Card
            key={programa.id}
            title={programa.materia_nombre}
            icon="description"
            action={
              programa.referencia_archivo ? (
                <a href={programa.referencia_archivo} target="_blank" rel="noopener noreferrer">
                  <Button size="sm" variant="secondary" icon="download">Descargar</Button>
                </a>
              ) : undefined
            }
          >
            <div style={{ fontSize: 13, color: 'var(--on-surface)', marginBottom: 6, fontWeight: 500 }}>
              {programa.programa_nombre}
            </div>
            <div style={{ fontSize: 12, color: 'var(--outline)', fontFamily: 'var(--font-mono)' }}>
              Publicado: {new Date(programa.fecha_publicacion).toLocaleDateString('es-AR')}
            </div>
            {!programa.referencia_archivo && (
              <div style={{ marginTop: 12, fontSize: 12, color: 'var(--outline)' }}>Sin archivo disponible</div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}

function PageHeader() {
  return (
    <div>
      <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Programas</h2>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Programas de estudio por materia</p>
    </div>
  );
}
