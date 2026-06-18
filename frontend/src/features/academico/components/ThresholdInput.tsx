import { useState, type ChangeEvent } from 'react';

interface ThresholdInputProps {
  value: number;
  onChange: (value: number) => void;
  onSave?: () => void;
  disabled?: boolean;
}

export function ThresholdInput({ value, onChange, onSave, disabled }: ThresholdInputProps) {
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    const parsed = parseInt(raw, 10);

    if (isNaN(parsed) || raw === '') {
      setError(null);
      onChange(0);
      return;
    }

    if (parsed < 1 || parsed > 100) {
      setError('El umbral debe ser un valor entre 1 y 100');
      return;
    }

    setError(null);
    onChange(parsed);
  };

  return (
    <div className="space-y-1">
      <label className="text-label-sm font-medium text-on-surface">Umbral de aprobación (%)</label>
      <div className="flex items-center gap-3">
        <input
          type="number"
          min={1}
          max={100}
          value={value || ''}
          onChange={handleChange}
          disabled={disabled}
          className={`w-24 rounded-lg border bg-surface-container-lowest px-3 py-2 text-label-md text-on-surface transition-colors focus:outline-none focus:ring-2 focus:ring-primary ${
            error ? 'border-error' : 'border-outline-variant'
          }`}
        />
        {onSave && value > 0 && !error && (
          <button
            type="button"
            onClick={onSave}
            disabled={disabled}
            className="rounded-lg bg-primary px-4 py-2 text-label-sm font-medium text-on-primary transition-colors hover:bg-primary/90 disabled:opacity-50"
          >
            Guardar umbral
          </button>
        )}
      </div>
      {error && <p className="text-label-sm text-error">{error}</p>}
    </div>
  );
}
