import { useState, useCallback } from 'react';
import type { PrediccionAbandono } from '../types/analytics';

interface ExportButtonsProps {
  dashboardRef: React.RefObject<HTMLDivElement | null>;
  prediccionData: PrediccionAbandono[] | undefined;
  disabled?: boolean;
}

export function ExportButtons({ dashboardRef, prediccionData, disabled }: ExportButtonsProps) {
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isExportingExcel, setIsExportingExcel] = useState(false);

  const handleExportPdf = useCallback(async () => {
    if (!dashboardRef.current) return;
    setIsExportingPdf(true);
    try {
      const html2canvas = (await import('html2canvas')).default;
      const { default: jsPDF } = await import('jspdf');

      const canvas = await html2canvas(dashboardRef.current, {
        backgroundColor: '#09090b',
        scale: 2,
      });
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('landscape', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('analytics-dashboard.pdf');
    } catch {
      // Silently fail
    } finally {
      setIsExportingPdf(false);
    }
  }, [dashboardRef]);

  const handleExportExcel = useCallback(async () => {
    if (!prediccionData || prediccionData.length === 0) return;
    setIsExportingExcel(true);
    try {
      const XLSX = await import('xlsx');
      const ws = XLSX.utils.json_to_sheet(
        prediccionData.map((d) => ({
          Alumno: d.alumno_nombre,
          Materia: d.materia,
          Promedio: `${d.promedio.toFixed(1)}%`,
          Atrasos: d.atrasos,
          Riesgo: d.riesgo.toUpperCase(),
        }))
      );
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'Prediccion');
      XLSX.writeFile(wb, 'analytics-prediccion-abandono.xlsx');
    } catch {
      // Silently fail
    } finally {
      setIsExportingExcel(false);
    }
  }, [prediccionData]);

  const btnBase = 'inline-flex items-center gap-1.5 rounded-lg border border-outline-variant px-3 py-2 text-label-sm font-medium text-on-surface-variant transition-colors hover:bg-surface-container-low hover:text-on-surface disabled:opacity-40 disabled:cursor-not-allowed';

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={handleExportPdf}
        disabled={disabled || isExportingPdf}
        className={btnBase}
      >
        {isExportingPdf ? (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-outline-variant border-t-primary" />
        ) : (
          <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
        )}
        Exportar PDF
      </button>
      <button
        type="button"
        onClick={handleExportExcel}
        disabled={disabled || isExportingExcel || !prediccionData || prediccionData.length === 0}
        className={btnBase}
      >
        {isExportingExcel ? (
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-outline-variant border-t-primary" />
        ) : (
          <span className="material-symbols-outlined text-[18px]">table_chart</span>
        )}
        Exportar Excel
      </button>
    </div>
  );
}
