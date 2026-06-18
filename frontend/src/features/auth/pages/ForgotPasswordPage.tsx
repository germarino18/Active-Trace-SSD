import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { useAuth } from '../hooks/useAuth';

const forgotSchema = z.object({
  email: z.string().email('Ingrese un email válido'),
});

type ForgotForm = z.infer<typeof forgotSchema>;

export function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ForgotForm>({
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
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-sm text-center">
          <span className="material-symbols-outlined text-tertiary text-4xl mb-2">mail</span>
          <h1 className="text-headline-md font-semibold text-on-surface">Solicitud enviada</h1>
          <p className="text-body-md text-on-surface-variant mt-2">{successMessage}</p>
          <Link to="/login" className="text-primary hover:underline mt-4 inline-block">Volver al inicio de sesión</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="material-symbols-outlined text-primary text-4xl mb-2">lock_reset</span>
          <h1 className="text-headline-md font-semibold text-on-surface">Recuperar contraseña</h1>
          <p className="text-body-md text-on-surface-variant mt-1">Ingrese su email para recibir un enlace de recuperación</p>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="email" className="text-label-md font-label-md text-on-surface mb-1 block">Email</label>
            <input
              id="email"
              type="email"
              {...register('email')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-on-surface placeholder:text-outline focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="usuario@example.com"
            />
            {errors.email && <p className="text-error text-label-sm mt-1">{errors.email.message}</p>}
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
            {isSubmitting ? <Spinner size="sm" /> : 'Enviar enlace de recuperación'}
          </button>
          <div className="text-center">
            <Link to="/login" className="text-label-sm text-primary hover:underline">Volver al inicio de sesión</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
