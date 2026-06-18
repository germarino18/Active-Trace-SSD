import { useAuth } from '@/features/auth/hooks/useAuth';

export function DashboardPage() {
  const { session } = useAuth();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-on-surface">Panel Principal</h2>
          {session.status === 'authenticated' && (
            <p className="text-body-md text-on-surface-variant mt-1">
              Bienvenido, {session.user.nombre} {session.user.apellido}
            </p>
          )}
        </div>
      </div>
      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-12 lg:col-span-8 rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
          <h3 className="text-label-md font-bold uppercase tracking-wider text-outline mb-4">Resumen Académico</h3>
          <p className="text-body-md text-on-surface-variant">El contenido del dashboard se agregará en próximas actualizaciones.</p>
        </div>
        <div className="col-span-12 lg:col-span-4 grid grid-rows-2 gap-6">
          <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline">Cursos Activos</h3>
            <p className="text-headline-lg font-semibold text-on-surface mt-2">—</p>
          </div>
          <div className="rounded-xl border border-outline-variant bg-surface-container-lowest p-md">
            <h3 className="text-label-md font-bold uppercase tracking-wider text-outline">Notificaciones</h3>
            <p className="text-headline-lg font-semibold text-on-surface mt-2">0</p>
          </div>
        </div>
      </div>
    </div>
  );
}
