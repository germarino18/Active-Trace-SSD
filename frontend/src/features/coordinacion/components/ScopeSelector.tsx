import type { AvisoScope } from '../types';

interface ScopeSelectorProps {
  scopeType: AvisoScope;
  scopeValue: string;
  onScopeTypeChange: (scope: AvisoScope) => void;
  onScopeValueChange: (value: string) => void;
}

const SCOPE_OPTIONS: { value: AvisoScope; label: string }[] = [
  { value: 'GLOBAL', label: 'Global' },
  { value: 'POR_MATERIA', label: 'Por Materia' },
  { value: 'POR_COHORTE', label: 'Por Cohorte' },
  { value: 'POR_ROL', label: 'Por Rol' },
];

const ROLE_OPTIONS = [
  { value: 'PROFESOR', label: 'Profesor' },
  { value: 'TUTOR', label: 'Tutor' },
  { value: 'NEXO', label: 'Nexo' },
  { value: 'COORDINADOR', label: 'Coordinador' },
  { value: 'ALUMNO', label: 'Alumno' },
];

export function ScopeSelector({
  scopeType,
  scopeValue,
  onScopeTypeChange,
  onScopeValueChange,
}: ScopeSelectorProps) {
  return (
    <div className="space-y-4">
      <div>
        <label className="mb-1 block text-label-sm text-on-surface-variant">Alcance</label>
        <select
          value={scopeType}
          onChange={(e) => {
            onScopeTypeChange(e.target.value as AvisoScope);
            onScopeValueChange('');
          }}
          className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
        >
          {SCOPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </div>

      {scopeType === 'POR_MATERIA' && (
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Materia</label>
          <input
            type="text"
            value={scopeValue}
            onChange={(e) => onScopeValueChange(e.target.value)}
            placeholder="ID de la materia"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
        </div>
      )}

      {scopeType === 'POR_COHORTE' && (
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Cohorte</label>
          <input
            type="text"
            value={scopeValue}
            onChange={(e) => onScopeValueChange(e.target.value)}
            placeholder="ID de la cohorte"
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none placeholder:text-outline focus:border-primary"
          />
        </div>
      )}

      {scopeType === 'POR_ROL' && (
        <div>
          <label className="mb-1 block text-label-sm text-on-surface-variant">Rol</label>
          <select
            value={scopeValue}
            onChange={(e) => onScopeValueChange(e.target.value)}
            className="w-full rounded-lg border border-outline-variant bg-surface-container px-3 py-2 text-body-sm text-on-surface outline-none focus:border-primary"
          >
            <option value="">Seleccioná un rol</option>
            {ROLE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
