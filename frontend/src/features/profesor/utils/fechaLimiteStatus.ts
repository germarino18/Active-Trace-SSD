/**
 * Pure helper: compute status for an actividad's fecha_limite relative to today.
 *
 * - 'vencida'  : fecha_limite < today (already past)
 * - 'proxima'  : today <= fecha_limite <= today + PROXIMA_DAYS_THRESHOLD (≤7 days away)
 * - null       : fecha_limite is null OR more than PROXIMA_DAYS_THRESHOLD days away
 *
 * Both parameters are ISO date strings ("YYYY-MM-DD"). today defaults to the
 * current date if not provided (useful for production use; overridable in tests).
 */

const PROXIMA_DAYS_THRESHOLD = 7;

export function getFechaLimiteStatus(
  fechaLimite: string | null,
  today?: string,
): 'vencida' | 'proxima' | null {
  if (!fechaLimite) return null;

  const todayStr = today ?? new Date().toISOString().slice(0, 10);
  const todayMs = Date.parse(todayStr);
  const limiteMs = Date.parse(fechaLimite);

  if (Number.isNaN(limiteMs)) return null;

  if (limiteMs < todayMs) return 'vencida';

  const diffDays = (limiteMs - todayMs) / (1000 * 60 * 60 * 24);
  if (diffDays <= PROXIMA_DAYS_THRESHOLD) return 'proxima';

  return null;
}
