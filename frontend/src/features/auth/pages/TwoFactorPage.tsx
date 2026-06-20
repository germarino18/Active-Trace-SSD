import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Button } from '@/shared/components/ds';
import { useAuth } from '../hooks/useAuth';

export function TwoFactorPage() {
  const { verify2fa } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [digits, setDigits] = useState(['', '', '', '', '', '']);

  const challengeToken = (location.state as { challengeToken?: string })?.challengeToken;

  const setDigit = (i: number, v: string) => {
    if (!/^\d?$/.test(v)) return;
    const next = [...digits];
    next[i] = v;
    setDigits(next);
    if (v && i < 5) {
      document.getElementById(`otp-${i + 1}`)?.focus();
    }
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!challengeToken) {
      setError('Sesión de verificación expirada. Volvé a iniciar sesión.');
      return;
    }
    const code = digits.join('');
    if (code.length !== 6) {
      setError('El código debe tener 6 dígitos');
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await verify2fa(challengeToken, code);
      navigate('/', { replace: true });
    } catch (err: unknown) {
      const apiError = err as { response?: { data?: { error?: { message?: string } } } };
      setError(apiError?.response?.data?.error?.message ?? 'Código inválido');
      setDigits(['', '', '', '', '', '']);
      document.getElementById('otp-0')?.focus();
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!challengeToken) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--background)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{ textAlign: 'center', maxWidth: 360 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: 'var(--error)', display: 'block', marginBottom: 12 }}>error</span>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: 'var(--on-surface)', margin: '0 0 8px' }}>Sesión no encontrada</h1>
          <p style={{ fontSize: 14, color: 'var(--on-surface-variant)', margin: '0 0 20px' }}>No hay una sesión de verificación activa. Por favor, iniciá sesión nuevamente.</p>
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
          <h1 style={{ margin: '0 0 4px', fontSize: 22, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Verificación 2FA</h1>
          <p style={{ margin: '0 0 24px', fontSize: 14, color: 'var(--on-surface-variant)' }}>Ingresá el código de 6 dígitos de tu app de autenticación.</p>

          <form onSubmit={onSubmit}>
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

          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Link to="/login" style={{ fontSize: 13, color: 'var(--primary)', textDecoration: 'none', fontWeight: 500 }}>Volver al inicio de sesión</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
