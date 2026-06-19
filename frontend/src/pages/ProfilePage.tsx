import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Card, Avatar, Badge, Input, Button, Select } from '@/shared/components/ds';
import { useProfileQuery, useProfileMutation } from '@/features/perfil/hooks/useProfile';
import { personalSchema, bankingSchema } from '@/features/perfil/profileSchema';
import type { PersonalForm, BankingForm } from '@/features/perfil/profileSchema';

const ROLE_LABELS: Record<string, string> = {
  ALUMNO: 'Alumno',
  PROFESOR: 'Docente',
  TUTOR: 'Tutor',
  COORDINADOR: 'Coordinador',
  NEXO: 'Nexo',
  ADMIN: 'Administrador',
  FINANZAS: 'Finanzas',
};

const MODALIDAD_OPTIONS = [
  { value: 'true', label: 'Factura' },
  { value: 'false', label: 'Liquidación' },
];

function SuccessBanner({ message }: { message: string }) {
  return (
    <div style={{ background: 'color-mix(in srgb, var(--tertiary) 14%, transparent)', border: '1px solid color-mix(in srgb, var(--tertiary) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px', marginBottom: 16 }}>
      <span style={{ fontSize: 13, color: 'var(--tertiary)' }}>{message}</span>
    </div>
  );
}

function ErrorBanner({ message }: { message: string }) {
  return (
    <div style={{ background: 'color-mix(in srgb, var(--error) 14%, transparent)', border: '1px solid color-mix(in srgb, var(--error) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px', marginBottom: 16 }}>
      <span style={{ fontSize: 13, color: 'var(--error)' }}>{message}</span>
    </div>
  );
}

export function ProfilePage() {
  const { session } = useAuth();
  const { data: profile, isLoading, isError, refetch } = useProfileQuery();
  const mutation = useProfileMutation();

  const [personalEditing, setPersonalEditing] = useState(false);
  const [personalSuccess, setPersonalSuccess] = useState(false);
  const [personalApiError, setPersonalApiError] = useState<string | null>(null);

  const [bankingEditing, setBankingEditing] = useState(false);
  const [bankingSuccess, setBankingSuccess] = useState(false);
  const [bankingApiError, setBankingApiError] = useState<string | null>(null);

  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const personalForm = useForm<PersonalForm>({ resolver: zodResolver(personalSchema) });
  const bankingForm = useForm<BankingForm>({ resolver: zodResolver(bankingSchema), defaultValues: { facturador: false } });

  useEffect(() => {
    if (profile) {
      personalForm.reset({
        nombre: profile.nombre ?? '',
        apellidos: profile.apellidos ?? '',
        dni: profile.dni ?? '',
        regional: profile.regional ?? '',
        legajo_profesional: profile.legajo_profesional ?? '',
      });
      bankingForm.reset({
        banco: profile.banco ?? '',
        cbu: profile.cbu ?? '',
        alias_cbu: profile.alias_cbu ?? '',
        facturador: profile.facturador ?? false,
      });
    }
  }, [profile]);

  if (session.status !== 'authenticated') return null;

  const { user } = session;

  const onPersonalSubmit = async (data: PersonalForm) => {
    setPersonalApiError(null);
    try {
      await mutation.mutateAsync(data);
      setPersonalEditing(false);
      setPersonalSuccess(true);
      setTimeout(() => setPersonalSuccess(false), 3000);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string; message?: string } } })?.response?.data?.detail
        ?? (err as { response?: { data?: { message?: string } } })?.response?.data?.message
        ?? 'Error al guardar los cambios';
      setPersonalApiError(msg);
    }
  };

  const onBankingSubmit = async (data: BankingForm) => {
    setBankingApiError(null);
    try {
      await mutation.mutateAsync(data);
      setBankingEditing(false);
      setBankingSuccess(true);
      setTimeout(() => setBankingSuccess(false), 3000);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string; message?: string } } })?.response?.data?.detail
        ?? (err as { response?: { data?: { message?: string } } })?.response?.data?.message
        ?? 'Error al guardar los cambios';
      setBankingApiError(msg);
    }
  };

  const cancelPersonal = () => {
    if (profile) {
      personalForm.reset({
        nombre: profile.nombre ?? '',
        apellidos: profile.apellidos ?? '',
        dni: profile.dni ?? '',
        regional: profile.regional ?? '',
        legajo_profesional: profile.legajo_profesional ?? '',
      });
    }
    setPersonalApiError(null);
    setPersonalEditing(false);
  };

  const cancelBanking = () => {
    if (profile) {
      bankingForm.reset({
        banco: profile.banco ?? '',
        cbu: profile.cbu ?? '',
        alias_cbu: profile.alias_cbu ?? '',
        facturador: profile.facturador ?? false,
      });
    }
    setBankingApiError(null);
    setBankingEditing(false);
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 800 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mi Perfil</h2>
          <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Cargando información...</p>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', padding: 48 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 32, color: 'var(--on-surface-variant)', animation: 'spin 1s linear infinite' }}>progress_activity</span>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 800 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mi Perfil</h2>
        </div>
        <Card>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, padding: '24px 0' }}>
            <span className="material-symbols-outlined" style={{ fontSize: 40, color: 'var(--error)' }}>error</span>
            <p style={{ margin: 0, color: 'var(--on-surface-variant)', fontSize: 14 }}>No se pudo cargar el perfil.</p>
            <Button variant="secondary" size="sm" onClick={() => refetch()}>Reintentar</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 800 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mi Perfil</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Información y configuración de tu cuenta</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 24, alignItems: 'start' }}>
        <Card>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 4 }}>
            <Avatar name={`${profile?.nombre ?? user.nombre} ${profile?.apellidos ?? user.apellido}`} size="lg" ring />
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--on-surface)', marginTop: 8 }}>
              {profile?.nombre ?? user.nombre} {profile?.apellidos ?? user.apellido}
            </div>
            <div style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>{profile?.email ?? user.email}</div>
            <div style={{ display: 'flex', gap: 6, marginTop: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
              {user.roles.map((role) => (
                <Badge key={role} tone="primary">{ROLE_LABELS[role.toUpperCase()] ?? role}</Badge>
              ))}
            </div>
          </div>
          <div style={{ height: 1, background: 'var(--outline-variant)', margin: '20px 0' }} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, fontSize: 13 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--outline)' }}>Tenant ID</span>
              <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--on-surface-variant)', fontSize: 12 }}>{user.tenant_id}</span>
            </div>
          </div>
        </Card>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Información personal */}
          <Card
            title="Información personal"
            icon="badge"
            action={
              !personalEditing
                ? <Button variant="secondary" size="sm" icon="edit" onClick={() => setPersonalEditing(true)}>Editar</Button>
                : <Button variant="ghost" size="sm" onClick={cancelPersonal}>Cancelar</Button>
            }
          >
            {personalSuccess && <SuccessBanner message="Datos personales actualizados correctamente." />}
            {personalApiError && <ErrorBanner message={personalApiError} />}
            <form onSubmit={personalForm.handleSubmit(onPersonalSubmit)} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <Input
                label="Nombre"
                readOnly={!personalEditing}
                error={personalForm.formState.errors.nombre?.message}
                {...personalForm.register('nombre')}
              />
              <Input
                label="Apellido/s"
                readOnly={!personalEditing}
                error={personalForm.formState.errors.apellidos?.message}
                {...personalForm.register('apellidos')}
              />
              <Input
                label="Email"
                icon="mail"
                value={profile?.email ?? ''}
                readOnly
                style={{ gridColumn: '1/-1' }}
                onChange={() => {}}
              />
              <Input
                label="CUIL"
                icon="fingerprint"
                value={profile?.cuil ?? ''}
                readOnly
                aria-readonly="true"
                onChange={() => {}}
              />
              <Input
                label="DNI"
                icon="id_card"
                readOnly={!personalEditing}
                error={personalForm.formState.errors.dni?.message}
                {...personalForm.register('dni')}
              />
              <Input
                label="Regional"
                readOnly={!personalEditing}
                error={personalForm.formState.errors.regional?.message}
                {...personalForm.register('regional')}
              />
              <Input
                label="Matrícula / Registro profesional"
                readOnly={!personalEditing}
                error={personalForm.formState.errors.legajo_profesional?.message}
                style={{ gridColumn: '1/-1' }}
                {...personalForm.register('legajo_profesional')}
              />
              {personalEditing && (
                <div style={{ gridColumn: '1/-1', display: 'flex', justifyContent: 'flex-end' }}>
                  <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
                    {mutation.isPending ? 'Guardando…' : 'Guardar cambios'}
                  </Button>
                </div>
              )}
            </form>
          </Card>

          {/* Datos bancarios */}
          <Card
            title="Datos bancarios"
            icon="account_balance"
            action={
              !bankingEditing
                ? <Button variant="secondary" size="sm" icon="edit" onClick={() => setBankingEditing(true)}>Editar</Button>
                : <Button variant="ghost" size="sm" onClick={cancelBanking}>Cancelar</Button>
            }
          >
            {bankingSuccess && <SuccessBanner message="Datos bancarios actualizados correctamente." />}
            {bankingApiError && <ErrorBanner message={bankingApiError} />}
            <form onSubmit={bankingForm.handleSubmit(onBankingSubmit)} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <Input
                label="Banco"
                icon="account_balance"
                readOnly={!bankingEditing}
                error={bankingForm.formState.errors.banco?.message}
                style={{ gridColumn: '1/-1' }}
                {...bankingForm.register('banco')}
              />
              <Input
                label="CBU"
                readOnly={!bankingEditing}
                error={bankingForm.formState.errors.cbu?.message}
                {...bankingForm.register('cbu')}
              />
              <Input
                label="Alias CBU"
                readOnly={!bankingEditing}
                error={bankingForm.formState.errors.alias_cbu?.message}
                {...bankingForm.register('alias_cbu')}
              />
              <div style={{ gridColumn: '1/-1' }}>
                <Select
                  label="Modalidad de cobro"
                  disabled={!bankingEditing}
                  options={MODALIDAD_OPTIONS}
                  value={String(bankingForm.watch('facturador'))}
                  onChange={(e) => bankingForm.setValue('facturador', e.target.value === 'true')}
                />
              </div>
              {bankingEditing && (
                <div style={{ gridColumn: '1/-1', display: 'flex', justifyContent: 'flex-end' }}>
                  <Button type="submit" variant="primary" size="sm" disabled={mutation.isPending}>
                    {mutation.isPending ? 'Guardando…' : 'Guardar cambios'}
                  </Button>
                </div>
              )}
            </form>
          </Card>

          {/* Cambiar contraseña */}
          <Card title="Cambiar contraseña" icon="lock">
            {passwordSuccess && <SuccessBanner message="Contraseña actualizada correctamente." />}
            <PasswordSection onSuccess={() => { setPasswordSuccess(true); setTimeout(() => setPasswordSuccess(false), 3000); }} />
          </Card>
        </div>
      </div>
    </div>
  );
}

import { z } from 'zod';

const passwordSchema = z
  .object({
    currentPassword: z.string().min(1, 'Ingresá tu contraseña actual'),
    newPassword: z.string().min(8, 'Mínimo 8 caracteres'),
    confirmPassword: z.string().min(1, 'Confirmá la nueva contraseña'),
  })
  .refine((d) => d.newPassword === d.confirmPassword, {
    message: 'Las contraseñas no coinciden',
    path: ['confirmPassword'],
  });

type PasswordForm = z.infer<typeof passwordSchema>;

function PasswordSection({ onSuccess }: { onSuccess: () => void }) {
  const passwordForm = useForm<PasswordForm>({ resolver: zodResolver(passwordSchema) });

  const onSubmit = async (_data: PasswordForm) => {
    onSuccess();
    passwordForm.reset();
  };

  return (
    <form onSubmit={passwordForm.handleSubmit(onSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Input
        label="Contraseña actual"
        icon="lock"
        type="password"
        placeholder="••••••••"
        error={passwordForm.formState.errors.currentPassword?.message}
        {...passwordForm.register('currentPassword')}
      />
      <Input
        label="Nueva contraseña"
        icon="lock_reset"
        type="password"
        placeholder="••••••••"
        helper="Mínimo 8 caracteres"
        error={passwordForm.formState.errors.newPassword?.message}
        {...passwordForm.register('newPassword')}
      />
      <Input
        label="Confirmar nueva contraseña"
        icon="lock_clock"
        type="password"
        placeholder="••••••••"
        error={passwordForm.formState.errors.confirmPassword?.message}
        {...passwordForm.register('confirmPassword')}
      />
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button type="submit" variant="primary" size="sm">Actualizar contraseña</Button>
      </div>
    </form>
  );
}
