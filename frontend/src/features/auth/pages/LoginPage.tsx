import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Card } from '@/shared/components/ui/Card';
import { Input } from '@/shared/components/ui/Input';
import { Button } from '@/shared/components/ui/Button';
import { Logo } from '@/shared/components/Logo';
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

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { tenant: '' },
  });

  const onSubmit = async (data: LoginForm) => {
    setError(null);
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
      setError(message ?? 'Credenciales inválidas');
    }
  };

  if (challenge) {
    return <TwoFactorChallenge challenge={challenge} />;
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background overflow-hidden p-4">
      {/* Decorative background glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="h-[500px] w-[500px] rounded-full bg-primary/3 blur-[120px]" />
      </div>
      <div className="relative w-full max-w-md">
        <div className="mb-8 text-center">
          <Logo size="lg" className="justify-center mb-3" />
          <h1 className="text-headline-md font-semibold text-on-surface">Iniciar sesión</h1>
          <p className="text-body-md text-on-surface-variant mt-1">Ingrese sus credenciales para acceder</p>
        </div>
        <Card padding="lg">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Input
                id="email"
                label="Email"
                type="email"
                placeholder="usuario@example.com"
                icon="mail"
                error={errors.email?.message}
                {...register('email')}
              />
              <Input
                id="password"
                label="Contraseña"
                type="password"
                placeholder="••••••••"
                icon="lock"
                error={errors.password?.message}
                {...register('password')}
              />
            </div>
            <Input
              id="tenant"
              label="Tenant"
              type="text"
              placeholder="ID del tenant"
              icon="business"
              error={errors.tenant?.message}
              {...register('tenant')}
            />
            {error && (
              <div className="rounded-lg border border-error/30 bg-error-container px-3.5 py-2.5">
                <p className="text-error text-label-sm">{error}</p>
              </div>
            )}
            <Button
              type="submit"
              loading={isSubmitting}
              className="w-full"
              size="lg"
            >
              Iniciar sesión
            </Button>
          </form>
        </Card>
        <div className="mt-5 text-center">
          <Link
            to="/forgot-password"
            className="text-label-sm text-primary hover:underline transition-colors"
          >
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
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <Logo size="lg" className="justify-center mb-3" />
          <h1 className="text-headline-md font-semibold text-on-surface">Verificación en dos pasos</h1>
          <p className="text-body-md text-on-surface-variant mt-1">Ingrese el código de su aplicación autenticadora</p>
        </div>
        <Card padding="lg">
          <form onSubmit={handleVerify} className="space-y-4">
            <div>
              <label htmlFor="code" className="block text-label-md font-label-md text-on-surface mb-1.5">
                Código
              </label>
              <input
                id="code"
                type="text"
                inputMode="numeric"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                className="w-full bg-surface-container-low border border-outline-variant rounded-xl px-4 py-2.5 text-center text-2xl tracking-[0.5em] text-on-surface placeholder:text-outline outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-all"
                placeholder="000000"
              />
              {error && <p className="text-error text-label-sm mt-1">{error}</p>}
            </div>
            <Button
              type="submit"
              loading={isSubmitting}
              disabled={code.length !== 6}
              className="w-full"
              size="lg"
            >
              Verificar
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
