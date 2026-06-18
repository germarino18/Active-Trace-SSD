import { useState, useCallback } from 'react';

const ALLOWED_EXTENSIONS = ['.csv', '.xlsx'];

interface UseFileUploadReturn {
  file: File | null;
  error: string | null;
  isInvalidExtension: boolean;
  handleFileSelect: (selectedFile: File | null) => void;
  reset: () => void;
}

function validateExtension(filename: string): boolean {
  const ext = filename.toLowerCase().slice(filename.lastIndexOf('.'));
  return ALLOWED_EXTENSIONS.includes(ext);
}

export function useFileUpload(): UseFileUploadReturn {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((selectedFile: File | null) => {
    setError(null);

    if (!selectedFile) {
      setFile(null);
      return;
    }

    if (!validateExtension(selectedFile.name)) {
      setError('Formato de archivo no soportado. Use .csv o .xlsx');
      return;
    }

    setFile(selectedFile);
  }, []);

  const reset = useCallback(() => {
    setFile(null);
    setError(null);
  }, []);

  return {
    file,
    error,
    isInvalidExtension: error !== null,
    handleFileSelect,
    reset,
  };
}
