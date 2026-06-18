import { useRef, type ChangeEvent } from 'react';

interface FileUploadAreaProps {
  onFileSelect: (file: File | null) => void;
  error?: string | null;
  accept?: string;
  isLoading?: boolean;
}

export function FileUploadArea({ onFileSelect, error, accept = '.csv,.xlsx', isLoading }: FileUploadAreaProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] ?? null;
    onFileSelect(selectedFile);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-lg transition-colors ${
        error
          ? 'border-error bg-error/5'
          : 'border-outline-variant bg-surface-container-lowest hover:border-primary hover:bg-primary/5'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
        disabled={isLoading}
        data-testid="file-input"
      />
      <span className="material-symbols-outlined text-[40px] text-outline mb-2">upload_file</span>
      <p className="text-body-md font-medium text-on-surface">Hacé clic para seleccionar un archivo</p>
      <p className="text-label-sm text-outline mt-1">Formatos aceptados: CSV, XLSX</p>
      {error && <p className="text-label-sm text-error mt-2">{error}</p>}
      {isLoading && (
        <div className="mt-3 flex items-center gap-2">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-outline-variant border-t-primary" role="status" />
          <span className="text-label-sm text-on-surface-variant">Subiendo archivo...</span>
        </div>
      )}
    </div>
  );
}
