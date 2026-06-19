import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Button, Input } from '@/shared/components/ds';
import { useAuth } from '../hooks/useAuth';
import type { TwoFactorChallenge } from '@/shared/types';

const loginSchema = z.object({
  email: z.string().email('Ingresá un email válido'),
  password: z.string().min(6, 'La contraseña debe tener al menos 6 caracteres'),
  tenant: z.string().min(1, 'El ID de institución es requerido'),
});

type LoginForm = z.infer<typeof loginSchema>;

const glowLeft: React.CSSProperties = {
  position: 'absolute', bottom: '-20%', left: '-10%',
  width: 600, height: 600, borderRadius: '50%', pointerEvents: 'none',
  background: 'color-mix(in srgb, var(--tertiary) 5%, transparent)',
  filter: 'blur(150px)',
};
const glowRight: React.CSSProperties = {
  position: 'absolute', top: '-20%', right: '-10%',
  width: 600, height: 600, borderRadius: '50%', pointerEvents: 'none',
  background: 'color-mix(in srgb, var(--primary) 8%, transparent)',
  filter: 'blur(140px)',
};

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [challenge, setChallenge] = useState<TwoFactorChallenge | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
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
      setError(message ?? 'Credenciales inválidas');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (challenge) {
    return <TwoFactorStep challenge={challenge} />;
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, position: 'relative', overflow: 'hidden' }}>
      <div style={glowRight} />
      <div style={glowLeft} />
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
          <h1 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Iniciar sesión</h1>
          <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>Ingresá a tu institución para continuar.</p>

          <form onSubmit={handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <Input
              label="Email"
              icon="mail"
              type="email"
              placeholder="usuario@example.com"
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              label="Contraseña"
              icon="lock"
              type="password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...register('password')}
            />
            <Input
              label="ID de Institución (tenant)"
              icon="domain"
              placeholder="ej: universidad-central"
              helper="Identificador provisto por tu institución"
              error={errors.tenant?.message}
              {...register('tenant')}
            />

            {error && (
              <div style={{ background: 'var(--error-container)', border: '1px solid color-mix(in srgb, var(--error) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px' }}>
                <span style={{ fontSize: 13, color: 'var(--on-error-container)' }}>{error}</span>
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: -4 }}>
              <Link to="/forgot-password" style={{ fontSize: 13, color: 'var(--primary)', textDecoration: 'none', fontWeight: 500 }}>¿Olvidaste tu contraseña?</Link>
            </div>

            <Button type="submit" variant="primary" size="lg" fullWidth disabled={isSubmitting} trailingIcon={isSubmitting ? undefined : 'arrow_forward'}>
              {isSubmitting ? 'Ingresando…' : 'Continuar'}
            </Button>
          </form>
        </div>

        <p style={{ textAlign: 'center', margin: '20px 0 0', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--outline)' }}>
          © {new Date().getFullYear()} Activia-Trace · Nexo Academic Systems
        </p>
      </div>
    </div>
  );
}

function TwoFactorStep({ challenge }: { challenge: TwoFactorChallenge }) {
  const { verify2fa } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [digits, setDigits] = useState(['', '', '', '', '', '']);

  const setDigit = (i: number, v: string) => {
    if (!/^\d?$/.test(v)) return;
    const next = [...digits];
    next[i] = v;
    setDigits(next);
    if (v && i < 5) {
      const el = document.getElementById(`otp-${i + 1}`);
      if (el) el.focus();
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = digits.join('');
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
      setDigits(['', '', '', '', '', '']);
      document.getElementById('otp-0')?.focus();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24, position: 'relative', overflow: 'hidden' }}>
      <div style={glowRight} />
      <div style={glowLeft} />
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
          <button
            type="button"
            onClick={() => window.history.back()}
            style={{ display: 'inline-flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', color: 'var(--on-surface-variant)', fontSize: 13, cursor: 'pointer', padding: 0, marginBottom: 16 }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 16 }}>arrow_back</span> Volver
          </button>

          <h1 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Verificación 2FA</h1>
          <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>Ingresá el código de 6 dígitos de tu app de autenticación.</p>

          <form onSubmit={handleVerify}>
            <div style={{ display: 'flex', gap: 8, justifyContent: 'space-between', marginBottom: 16 }}>
              {digits.map((d, i) => (
                <input
                  key={i}
                  id={`otp-${i}`}
                  value={d}
                  onChange={(e) => setDigit(i, e.target.value)}
                  maxLength={1}
                  inputMode="numeric"
                  style={{
                    width: 48, height: 56, textAlign: 'center', fontSize: 22, fontWeight: 700,
                    background: 'var(--surface-container-low)', color: 'var(--on-surface)',
                    border: `1px solid ${d ? 'var(--primary)' : 'var(--outline-variant)'}`,
                    borderRadius: 'var(--radius-md)', outline: 'none', fontFamily: 'var(--font-mono)',
                  }}
                />
              ))}
            </div>

            {error && (
              <div style={{ background: 'var(--error-container)', border: '1px solid color-mix(in srgb, var(--error) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px', marginBottom: 16 }}>
                <span style={{ fontSize: 13, color: 'var(--on-error-container)' }}>{error}</span>
              </div>
            )}

            <Button type="submit" variant="primary" size="lg" fullWidth disabled={isSubmitting || digits.join('').length !== 6}>
              {isSubmitting ? 'Verificando…' : 'Verificar e ingresar'}
            </Button>
          </form>
        </div>

        <p style={{ textAlign: 'center', margin: '20px 0 0', fontSize: 11, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--outline)' }}>
          © {new Date().getFullYear()} Activia-Trace · Nexo Academic Systems
        </p>
      </div>
    </div>
  );
}
