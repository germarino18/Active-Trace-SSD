import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Button, Input } from '@/shared/components/ds';
import { useAuth } from '../hooks/useAuth';

const forgotSchema = z.object({
  email: z.string().email('Ingresá un email válido'),
});

type ForgotForm = z.infer<typeof forgotSchema>;

export function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<ForgotForm>({
    resolver: zodResolver(forgotSchema),
  });

  const onSubmit = async (data: ForgotForm) => {
    setError(null);
    setIsSubmitting(true);
    try {
      const message = await forgotPassword(data.email);
      setSuccessMessage(message);
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(apiError?.response?.data?.error?.message ?? 'Error al procesar la solicitud');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (successMessage) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{ textAlign: 'center', maxWidth: 360 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--tertiary)', display: 'block', marginBottom: 12, fontVariationSettings: "'FILL' 1" }}>mark_email_read</span>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--on-surface)', margin: '0 0 8px' }}>Revisá tu email</h1>
          <p style={{ fontSize: 14, color: 'var(--on-surface-variant)', margin: '0 0 20px' }}>{successMessage}</p>
          <Link to="/login" style={{ fontSize: 13, color: 'var(--primary)', textDecoration: 'none', fontWeight: 500 }}>Volver al inicio de sesión</Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, position: 'relative', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', top: '-20%', right: '-10%', width: 600, height: 600, borderRadius: '50%', pointerEvents: 'none', background: 'color-mix(in srgb, var(--primary) 8%, transparent)', filter: 'blur(140px)' }} />
      <div style={{ width: 400, maxWidth: '100%', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, justifyContent: 'center', marginBottom: 28 }}>
          <div style={{ width: 44, height: 44, background: 'var(--primary)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--on-primary)' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 26, fontVariationSettings: "'FILL' 1" }}>analytics</span>
          </div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--on-surface)' }}>Activia-Trace</div>
            <div style={{ fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--on-surface-variant)', opacity: 0.6 }}>Academic Management</div>
          </div>
        </div>

        <div style={{ background: 'var(--surface-container)', border: '1px solid var(--outline-variant)', borderRadius: 'var(--radius-lg)', padding: 28 }}>
          <h1 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Recuperar contraseña</h1>
          <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>Ingresá tu email y te enviamos un enlace de recuperación.</p>

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <Input
              label="Email"
              icon="mail"
              type="email"
              placeholder="usuario@example.com"
              error={errors.email?.message}
              {...register('email')}
            />

            {error && (
              <div style={{ background: 'var(--error-container)', border: '1px solid color-mix(in srgb, var(--error) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px' }}>
                <span style={{ fontSize: 13, color: 'var(--on-error-container)' }}>{error}</span>
              </div>
            )}

            <Button type="submit" variant="primary" size="lg" fullWidth disabled={isSubmitting}>
              {isSubmitting ? 'Enviando…' : 'Enviar enlace de recuperación'}
            </Button>

            <div style={{ textAlign: 'center' }}>
              <Link to="/login" style={{ fontSize: 13, color: 'var(--primary)', textDecoration: 'none', fontWeight: 500 }}>Volver al inicio de sesión</Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
