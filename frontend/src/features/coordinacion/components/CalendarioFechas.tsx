import { useMemo } from 'react';
import type { FechaAcademica, TipoFechaAcademica } from '../types';

interface CalendarioFechasProps {
  fechas: FechaAcademica[];
  currentMonth: Date;
  onMonthChange: (date: Date) => void;
}

const tipoColor: Record<TipoFechaAcademica, string> = {
  Parcial: 'bg-blue-500',
  TP: 'bg-green-500',
  Coloquio: 'bg-purple-500',
};

const tipoLabel: Record<TipoFechaAcademica, string> = {
  Parcial: 'P',
  TP: 'TP',
  Coloquio: 'C',
};

const DAYS = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
const MONTHS = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

export function CalendarioFechas({ fechas, currentMonth, onMonthChange }: CalendarioFechasProps) {
  const calendarDays = useMemo(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startPad = firstDay.getDay();
    const daysInMonth = lastDay.getDate();

    const days: { date: Date; isCurrentMonth: boolean; fechas: FechaAcademica[] }[] = [];

    for (let i = 0; i < startPad; i++) {
      const prevDate = new Date(year, month, -startPad + i + 1);
      days.push({ date: prevDate, isCurrentMonth: false, fechas: [] });
    }

    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(year, month, d);
      const dateStr = date.toISOString().split('T')[0];
      const dayFechas = fechas.filter((f) => f.fecha.startsWith(dateStr));
      days.push({ date, isCurrentMonth: true, fechas: dayFechas });
    }

    const remaining = (42 - days.length) % 7;
    if (remaining > 0) {
      for (let i = 1; i <= remaining; i++) {
        const nextDate = new Date(year, month + 1, i);
        days.push({ date: nextDate, isCurrentMonth: false, fechas: [] });
      }
    }

    return days;
  }, [fechas, currentMonth]);

  const prevMonth = () => onMonthChange(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1));
  const nextMonth = () => onMonthChange(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1));

  const todayStr = new Date().toISOString().split('T')[0];

  return (
    <div className="rounded-xl border border-outline-variant bg-surface-container-lowest overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant">
        <button
          type="button"
          onClick={prevMonth}
          className="rounded-lg p-1.5 text-on-surface-variant hover:bg-surface-container-low transition-colors"
        >
          <span className="material-symbols-outlined text-[20px]">chevron_left</span>
        </button>
        <h3 className="text-label-md font-medium text-on-surface">
          {MONTHS[currentMonth.getMonth()]} {currentMonth.getFullYear()}
        </h3>
        <button
          type="button"
          onClick={nextMonth}
          className="rounded-lg p-1.5 text-on-surface-variant hover:bg-surface-container-low transition-colors"
        >
          <span className="material-symbols-outlined text-[20px]">chevron_right</span>
        </button>
      </div>

      <div className="grid grid-cols-7">
        {DAYS.map((day) => (
          <div
            key={day}
            className="px-1 py-2 text-center text-label-xs font-medium text-on-surface-variant border-b border-outline-variant/50"
          >
            {day}
          </div>
        ))}

        {calendarDays.map((day, i) => {
          const dateStr = day.date.toISOString().split('T')[0];
          const isToday = dateStr === todayStr;

          return (
            <div
              key={i}
              className={`min-h-[72px] border-b border-r border-outline-variant/30 p-1 ${
                day.isCurrentMonth ? 'bg-surface-container-lowest' : 'bg-surface-container-low/30'
              } ${isToday ? 'ring-1 ring-primary/40 ring-inset' : ''}`}
            >
              <span
                className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-label-xs ${
                  isToday
                    ? 'bg-primary text-on-primary font-medium'
                    : 'text-on-surface-variant'
                }`}
              >
                {day.date.getDate()}
              </span>
              <div className="mt-1 space-y-0.5">
                {day.fechas.slice(0, 3).map((f) => (
                  <div
                    key={f.id}
                    className={`${tipoColor[f.tipo]} rounded px-1 py-0.5 text-[10px] leading-tight text-white truncate`}
                    title={`${f.titulo} (${f.tipo})`}
                  >
                    {tipoLabel[f.tipo]} {f.instancia}
                  </div>
                ))}
                {day.fechas.length > 3 && (
                  <span className="text-[10px] text-on-surface-variant">+{day.fechas.length - 3} más</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
