import { useAuth } from '@/features/auth/hooks/useAuth';

export function ProfilePage() {
  const { session } = useAuth();

  if (session.status !== 'authenticated') return null;

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h2 className="font-headline-lg text-headline-lg text-on-surface">Mi Perfil</h2>
        <p className="text-body-md text-on-surface-variant mt-1">Información de su cuenta</p>
      </div>
      <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
        <div className="space-y-4">
          <div>
            <p className="text-label-sm text-outline">Nombre</p>
            <p className="text-body-md text-on-surface">{session.user.nombre} {session.user.apellido}</p>
          </div>
          <div>
            <p className="text-label-sm text-outline">Email</p>
            <p className="text-body-md text-on-surface">{session.user.email}</p>
          </div>
          <div>
            <p className="text-label-sm text-outline">Roles</p>
            <p className="text-body-md text-on-surface">{session.user.roles.join(', ') || '—'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
