import { Link } from 'react-router-dom';

export function ForbiddenPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="text-center max-w-md">
        <h1 className="font-headline-xl text-headline-xl font-bold text-on-surface">403</h1>
        <p className="text-body-lg text-on-surface-variant mt-2">No tiene permisos para acceder a esta sección</p>
        <Link to="/dashboard" className="text-primary hover:underline mt-4 inline-block">
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
