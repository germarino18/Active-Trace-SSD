import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { useAuth } from '../hooks/useAuth';

const resetSchema = z
  .object({
    password: z.string().min(8, 'La contraseña debe tener al menos 8 caracteres'),
    confirmPassword: z.string().min(1, 'Debe confirmar la contraseña'),
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

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetForm>({
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
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-sm text-center">
          <span className="material-symbols-outlined text-error text-4xl mb-2">error</span>
          <h1 className="text-headline-md font-semibold text-on-surface">Enlace inválido</h1>
          <p className="text-body-md text-on-surface-variant mt-2">El enlace de recuperación es inválido o ha expirado.</p>
          <Link to="/forgot-password" className="text-primary hover:underline mt-4 inline-block">Solicitar nuevo enlace</Link>
        </div>
      </div>
    );
  }

  if (successMessage) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-sm text-center">
          <span className="material-symbols-outlined text-tertiary text-4xl mb-2">check_circle</span>
          <h1 className="text-headline-md font-semibold text-on-surface">Contraseña actualizada</h1>
          <p className="text-body-md text-on-surface-variant mt-2">{successMessage}</p>
          <p className="text-body-md text-on-surface-variant mt-1">Redirigiendo al inicio de sesión...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="material-symbols-outlined text-primary text-4xl mb-2">password</span>
          <h1 className="text-headline-md font-semibold text-on-surface">Nueva contraseña</h1>
          <p className="text-body-md text-on-surface-variant mt-1">Ingrese su nueva contraseña</p>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="password" className="text-label-md font-label-md text-on-surface mb-1 block">Nueva contraseña</label>
            <input
              id="password"
              type="password"
              {...register('password')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-on-surface placeholder:text-outline focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="••••••••"
            />
            {errors.password && <p className="text-error text-label-sm mt-1">{errors.password.message}</p>}
          </div>
          <div>
            <label htmlFor="confirmPassword" className="text-label-md font-label-md text-on-surface mb-1 block">Confirmar contraseña</label>
            <input
              id="confirmPassword"
              type="password"
              {...register('confirmPassword')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-on-surface placeholder:text-outline focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="••••••••"
            />
            {errors.confirmPassword && <p className="text-error text-label-sm mt-1">{errors.confirmPassword.message}</p>}
          </div>
          {error && (
            <div className="rounded-lg border border-error/30 bg-error-container px-3 py-2">
              <p className="text-error text-label-sm">{error}</p>
            </div>
          )}
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex w-full items-center justify-center rounded-xl bg-primary px-4 py-2.5 font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {isSubmitting ? <Spinner size="sm" /> : 'Restablecer contraseña'}
          </button>
          <div className="text-center">
            <Link to="/login" className="text-label-sm text-primary hover:underline">Volver al inicio de sesión</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
