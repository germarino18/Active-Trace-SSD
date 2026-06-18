import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { useAuth } from '../hooks/useAuth';

const twoFactorSchema = z.object({
  code: z.string().length(6, 'El código debe tener 6 dígitos').regex(/^\d{6}$/, 'Solo dígitos permitidos'),
});

type TwoFactorForm = z.infer<typeof twoFactorSchema>;

export function TwoFactorPage() {
  const { verify2fa } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const challengeToken = (location.state as { challengeToken?: string })?.challengeToken;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TwoFactorForm>({
    resolver: zodResolver(twoFactorSchema),
  });

  const onSubmit = async (data: TwoFactorForm) => {
    if (!challengeToken) {
      setError('Sesión de verificación expirada. Vuelva a iniciar sesión.');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await verify2fa(challengeToken, data.code);
      navigate('/dashboard', { replace: true });
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(apiError?.response?.data?.error?.message ?? 'Código inválido');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!challengeToken) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-sm text-center">
          <h1 className="text-headline-md font-semibold text-on-surface">Verificación requerida</h1>
          <p className="text-body-md text-on-surface-variant mt-2">
            No se encontró una sesión de verificación activa. Por favor, inicie sesión nuevamente.
          </p>
          <Link to="/login" className="text-primary hover:underline mt-4 inline-block">Volver al inicio de sesión</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="material-symbols-outlined text-primary text-4xl mb-2">verified</span>
          <h1 className="text-headline-md font-semibold text-on-surface">Verificación en dos pasos</h1>
          <p className="text-body-md text-on-surface-variant mt-1">Ingrese el código de su aplicación autenticadora</p>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="code" className="text-label-md font-label-md text-on-surface mb-1 block">Código</label>
            <input
              id="code"
              type="text"
              inputMode="numeric"
              maxLength={6}
              {...register('code')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-center text-2xl tracking-widest text-on-surface focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="000000"
            />
            {errors.code && <p className="text-error text-label-sm mt-1">{errors.code.message}</p>}
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
            {isSubmitting ? <Spinner size="sm" /> : 'Verificar'}
          </button>
          <div className="text-center">
            <Link to="/login" className="text-label-sm text-primary hover:underline">Volver al inicio de sesión</Link>
          </div>
        </form>
      </div>
    </div>
  );
}
