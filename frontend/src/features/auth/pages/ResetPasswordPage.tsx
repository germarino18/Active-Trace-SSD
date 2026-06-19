import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { Button, Input } from '@/shared/components/ds';
import { useAuth } from '../hooks/useAuth';

const resetSchema = z
  .object({
    password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
    confirmPassword: z.string().min(1, 'Debés confirmar la contraseña'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Las contraseñas no coinciden',
    path: ['confirmPassword'],
  });

type ResetForm = z.infer<typeof resetSchema>;

export function ResetPasswordPage() {
  const { resetPassword } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const token = searchParams.get('token');

  const { register, handleSubmit, formState: { errors } } = useForm<ResetForm>({
    resolver: zodResolver(resetSchema),
  });

  const onSubmit = async (data: ResetForm) => {
    if (!token) {
      setError('Token de recuperación inválido o expirado');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const message = await resetPassword(token, data.password);
      setSuccessMessage(message);
      setTimeout(() => navigate('/login', { replace: true }), 3000);
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(apiError?.response?.data?.error?.message ?? 'Error al restablecer la contraseña');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!token) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{ textAlign: 'center', maxWidth: 360 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--error)', display: 'block', marginBottom: 12 }}>error</span>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--on-surface)', margin: '0 0 8px' }}>Enlace inválido</h1>
          <p style={{ fontSize: 14, color: 'var(--on-surface-variant)', margin: '0 0 20px' }}>El enlace de recuperación es inválido o ha expirado.</p>
          <Link to="/forgot-password" style={{ fontSize: 13, color: 'var(--primary)', textDecoration: 'none', fontWeight: 500 }}>Solicitar nuevo enlace</Link>
        </div>
      </div>
    );
  }

  if (successMessage) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{ textAlign: 'center', maxWidth: 360 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--tertiary)', display: 'block', marginBottom: 12, fontVariationSettings: "'FILL' 1" }}>check_circle</span>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--on-surface)', margin: '0 0 8px' }}>Contraseña actualizada</h1>
          <p style={{ fontSize: 14, color: 'var(--on-surface-variant)', margin: '0 0 4px' }}>{successMessage}</p>
          <p style={{ fontSize: 13, color: 'var(--outline)' }}>Redirigiendo al inicio de sesión…</p>
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
          <h1 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Nueva contraseña</h1>
          <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>Elegí una contraseña segura para tu cuenta.</p>

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <Input
              label="Nueva contraseña"
              icon="lock"
              type="password"
              placeholder="••••••••"
              helper="Mínimo 8 caracteres"
              error={errors.password?.message}
              {...register('password')}
            />
            <Input
              label="Confirmar contraseña"
              icon="lock_clock"
              type="password"
              placeholder="••••••••"
              error={errors.confirmPassword?.message}
              {...register('confirmPassword')}
            />

            {error && (
              <div style={{ background: 'var(--error-container)', border: '1px solid color-mix(in srgb, var(--error) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px' }}>
                <span style={{ fontSize: 13, color: 'var(--on-error-container)' }}>{error}</span>
              </div>
            )}

            <Button type="submit" variant="primary" size="lg" fullWidth disabled={isSubmitting}>
              {isSubmitting ? 'Guardando…' : 'Restablecer contraseña'}
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
