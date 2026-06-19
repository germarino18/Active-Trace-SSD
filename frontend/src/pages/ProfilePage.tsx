import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Card, Avatar, Badge, Input, Button } from '@/shared/components/ds';

const profileSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  apellido: z.string().min(1, 'El apellido es requerido'),
});

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

type ProfileForm = z.infer<typeof profileSchema>;
type PasswordForm = z.infer<typeof passwordSchema>;

const ROLE_LABELS: Record<string, string> = {
  ALUMNO: 'Alumno',
  PROFESOR: 'Docente',
  TUTOR: 'Tutor',
  COORDINADOR: 'Coordinador',
  NEXO: 'Nexo',
  ADMIN: 'Administrador',
  FINANZAS: 'Finanzas',
};

export function ProfilePage() {
  const { session } = useAuth();
  const [editing, setEditing] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const profileForm = useForm<ProfileForm>({ resolver: zodResolver(profileSchema) });
  const passwordForm = useForm<PasswordForm>({ resolver: zodResolver(passwordSchema) });

  if (session.status !== 'authenticated') return null;

  const { user } = session;

  const onProfileSubmit = async (_data: ProfileForm) => {
    setProfileSuccess(true);
    setEditing(false);
    setTimeout(() => setProfileSuccess(false), 3000);
  };

  const onPasswordSubmit = async (_data: PasswordForm) => {
    setPasswordSuccess(true);
    passwordForm.reset();
    setTimeout(() => setPasswordSuccess(false), 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 800 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, letterSpacing: '-0.01em', color: 'var(--on-surface)' }}>Mi Perfil</h2>
        <p style={{ margin: '4px 0 0', fontSize: 14, color: 'var(--on-surface-variant)' }}>Información y configuración de tu cuenta</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 24, alignItems: 'start' }}>
        <Card>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: 4 }}>
            <Avatar name={`${user.nombre} ${user.apellido}`} size="lg" ring />
            <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--on-surface)', marginTop: 8 }}>
              {user.nombre} {user.apellido}
            </div>
            <div style={{ fontSize: 13, color: 'var(--on-surface-variant)' }}>{user.email}</div>
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
          <Card
            title="Información de la cuenta"
            icon="badge"
            action={
              !editing
                ? <Button variant="secondary" size="sm" icon="edit" onClick={() => setEditing(true)}>Editar</Button>
                : <Button variant="ghost" size="sm" onClick={() => setEditing(false)}>Cancelar</Button>
            }
          >
            {profileSuccess && (
              <div style={{ background: 'color-mix(in srgb, var(--tertiary) 14%, transparent)', border: '1px solid color-mix(in srgb, var(--tertiary) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px', marginBottom: 16 }}>
                <span style={{ fontSize: 13, color: 'var(--tertiary)' }}>Perfil actualizado correctamente.</span>
              </div>
            )}
            <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <Input
                label="Nombre"
                defaultValue={user.nombre}
                readOnly={!editing}
                error={profileForm.formState.errors.nombre?.message}
                {...profileForm.register('nombre')}
              />
              <Input
                label="Apellido"
                defaultValue={user.apellido}
                readOnly={!editing}
                error={profileForm.formState.errors.apellido?.message}
                {...profileForm.register('apellido')}
              />
              <Input label="Email" icon="mail" value={user.email} readOnly style={{ gridColumn: '1/-1' }} />
              {editing && (
                <div style={{ gridColumn: '1/-1', display: 'flex', justifyContent: 'flex-end' }}>
                  <Button type="submit" variant="primary" size="sm">Guardar cambios</Button>
                </div>
              )}
            </form>
          </Card>

          <Card title="Cambiar contraseña" icon="lock">
            {passwordSuccess && (
              <div style={{ background: 'color-mix(in srgb, var(--tertiary) 14%, transparent)', border: '1px solid color-mix(in srgb, var(--tertiary) 30%, transparent)', borderRadius: 'var(--radius-md)', padding: '8px 12px', marginBottom: 16 }}>
                <span style={{ fontSize: 13, color: 'var(--tertiary)' }}>Contraseña actualizada correctamente.</span>
              </div>
            )}
            <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
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
          </Card>
        </div>
      </div>
    </div>
  );
}
