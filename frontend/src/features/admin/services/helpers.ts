/**
 * Normaliza las respuestas del backend al formato { items, total } que espera el frontend.
 * El backend devuelve { value: T[], Count: number } o T[] directamente.
 */
export function normalizeListResponse<T>(data: unknown): { items: T[]; total: number } {
  if (Array.isArray(data)) {
    return { items: data as T[], total: data.length };
  }
  const d = data as Record<string, unknown>;
  const value = d.value as T[] | undefined;
  const count = d.Count as number | undefined;
  return {
    items: value ?? [],
    total: count ?? (Array.isArray(value) ? value.length : 0),
  };
}
