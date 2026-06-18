import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Spinner } from '@/shared/components/Spinner';
import { useAuth } from '../hooks/useAuth';
import type { TwoFactorChallenge } from '@/shared/types';

const loginSchema = z.object({
  email: z.string().email('Ingrese un email válido'),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
  tenant: z.string().min(1, 'El tenant es requerido'),
});

type LoginForm = z.infer<typeof loginSchema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [challenge, setChallenge] = useState<TwoFactorChallenge | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { tenant: '' },
  });

  const onSubmit = async (data: LoginForm) => {
    setError(null);
    setIsSubmitting(true);
    try {
      const result = await login(data.email, data.password, data.tenant);
      if ('requires_2fa' in result && result.requires_2fa === true) {
        setChallenge(result);
      } else {
        const redirect = searchParams.get('redirect') || '/dashboard';
        navigate(redirect, { replace: true });
      }
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { error?: { message?: string } } } };
      const message = apiError?.response?.data?.error?.message;
      if (message) {
        setError(message);
      } else {
        setError('Credenciales inválidas');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (challenge) {
    return <TwoFactorChallenge challenge={challenge} />;
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <span className="material-symbols-outlined text-on-primary text-2xl">analytics</span>
          </div>
          <h1 className="text-headline-md font-semibold text-on-surface">Activia-Trace</h1>
          <p className="text-body-md text-on-surface-variant mt-1">Iniciar sesión</p>
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
          <div>
            <label htmlFor="password" className="text-label-md font-label-md text-on-surface mb-1 block">Contraseña</label>
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
            <label htmlFor="tenant" className="text-label-md font-label-md text-on-surface mb-1 block">Tenant</label>
            <input
              id="tenant"
              type="text"
              {...register('tenant')}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-on-surface placeholder:text-outline focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="ID del tenant"
            />
            {errors.tenant && <p className="text-error text-label-sm mt-1">{errors.tenant.message}</p>}
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
            {isSubmitting ? <Spinner size="sm" /> : 'Iniciar sesión'}
          </button>
        </form>
        <div className="mt-4 text-center">
          <Link to="/forgot-password" className="text-label-sm text-primary hover:underline">
            ¿Olvidó su contraseña?
          </Link>
        </div>
      </div>
    </div>
  );
}

function TwoFactorChallenge({ challenge }: { challenge: TwoFactorChallenge }) {
  const { verify2fa } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [code, setCode] = useState('');

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (code.length !== 6) {
      setError('El código debe tener 6 dígitos');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await verify2fa(challenge.challenge_token, code, challenge.temp_token);
      const redirect = searchParams.get('redirect') || '/dashboard';
      navigate(redirect, { replace: true });
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(apiError?.response?.data?.error?.message ?? 'Código inválido');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <span className="material-symbols-outlined text-on-primary text-2xl">verified</span>
          </div>
          <h1 className="text-headline-md font-semibold text-on-surface">Verificación en dos pasos</h1>
          <p className="text-body-md text-on-surface-variant mt-1">Ingrese el código de su aplicación autenticadora</p>
        </div>
        <form onSubmit={handleVerify} className="space-y-4">
          <div>
            <label htmlFor="code" className="text-label-md font-label-md text-on-surface mb-1 block">Código</label>
            <input
              id="code"
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
              className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-center text-2xl tracking-widest text-on-surface focus:ring-2 focus:ring-primary focus:outline-none"
              placeholder="000000"
            />
            {error && <p className="text-error text-label-sm mt-1">{error}</p>}
          </div>
          <button
            type="submit"
            disabled={isSubmitting || code.length !== 6}
            className="flex w-full items-center justify-center rounded-xl bg-primary px-4 py-2.5 font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            {isSubmitting ? <Spinner size="sm" /> : 'Verificar'}
          </button>
        </form>
      </div>
    </div>
  );
}
