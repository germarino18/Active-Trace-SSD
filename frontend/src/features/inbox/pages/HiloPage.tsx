import { useParams, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState, Button, Textarea } from '@/shared/components/ds';
import { useHilo } from '../hooks/useHilo';
import { useResponder } from '../hooks/useResponder';

const respuestaSchema = z.object({
  contenido: z.string().min(1, 'La respuesta no puede estar vacía').max(2000, 'Máximo 2000 caracteres'),
});

type RespuestaForm = z.infer<typeof respuestaSchema>;

export function HiloPage() {
  const { id } = useParams<{ id: string }>();
  const { mensajes, isLoading, error } = useHilo(id!);
  const responderMutation = useResponder(id!);

  const { register, handleSubmit, reset, formState: { errors, isValid } } = useForm<RespuestaForm>({
    resolver: zodResolver(respuestaSchema),
    mode: 'onChange',
  });

  if (isLoading) {
    return <div className="flex justify-center py-12"><Spinner size="lg" /></div>;
  }

  if (error) {
    return (
      <EmptyState
        icon="error"
        title="Error al cargar mensajes"
        action={
          <Link to="/inbox">
            <Button variant="secondary">Volver a mensajes</Button>
          </Link>
        }
      />
    );
  }

  if (mensajes.length === 0) {
    return (
      <EmptyState
        icon="search_off"
        title="Mensaje no encontrado"
        action={
          <Link to="/inbox">
            <Button variant="secondary">Volver a mensajes</Button>
          </Link>
        }
      />
    );
  }

  const onSubmit = (data: RespuestaForm) => {
    responderMutation.mutate(data, { onSuccess: () => reset() });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--on-surface-variant)' }}>
        <Link
          to="/inbox"
          style={{ color: 'var(--on-surface-variant)', textDecoration: 'none' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--on-surface-variant)')}
        >
          Mensajes
        </Link>
        <span className="material-symbols-outlined" style={{ fontSize: 16 }}>chevron_right</span>
        <span style={{ color: 'var(--on-surface)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {mensajes[0]?.remitente ?? 'Hilo'}
        </span>
      </div>

      <h2 style={{ margin: 0, fontSize: 28, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>
        {mensajes[0]?.remitente}
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {mensajes.map((msg) => (
          <div
            key={msg.id}
            style={{
              background: 'var(--surface-container-lowest)', borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--outline-variant)', padding: 20,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 'var(--radius-full)',
                background: 'color-mix(in srgb, var(--primary) 20%, transparent)',
                color: 'var(--primary)', display: 'flex', alignItems: 'center',
                justifyContent: 'center', fontSize: 12, fontWeight: 700, flexShrink: 0,
              }}>
                {msg.remitente.charAt(0).toUpperCase()}
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--on-surface)' }}>{msg.remitente}</div>
                <div style={{ fontSize: 12, color: 'var(--outline)', fontFamily: 'var(--font-mono)' }}>
                  {new Date(msg.fecha).toLocaleDateString('es-AR', {
                    day: 'numeric', month: 'long', year: 'numeric',
                    hour: '2-digit', minute: '2-digit',
                  })}
                </div>
              </div>
            </div>
            <p style={{ margin: 0, fontSize: 14, color: 'var(--on-surface-variant)', lineHeight: '1.6', whiteSpace: 'pre-line' }}>
              {msg.contenido}
            </p>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <Textarea
          label="Tu respuesta"
          placeholder="Escribí tu respuesta..."
          rows={4}
          error={errors.contenido?.message}
          {...register('contenido')}
        />

        {responderMutation.isError && (
          <p style={{ margin: 0, fontSize: 13, color: 'var(--error)', textAlign: 'right' }}>
            Error al enviar. Intentá de nuevo.
          </p>
        )}
        {responderMutation.isSuccess && (
          <p style={{ margin: 0, fontSize: 13, color: 'var(--tertiary)', textAlign: 'right' }}>
            Respuesta enviada correctamente
          </p>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <Link to="/inbox">
            <Button variant="secondary">Volver</Button>
          </Link>
          <Button
            type="submit"
            variant="primary"
            icon="send"
            disabled={!isValid || responderMutation.isPending}
          >
            {responderMutation.isPending ? 'Enviando…' : 'Enviar respuesta'}
          </Button>
        </div>
      </form>
    </div>
  );
}
