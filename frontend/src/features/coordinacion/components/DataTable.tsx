import { useState } from 'react';
import { Spinner } from '@/shared/components/Spinner';
import { EmptyState } from '@/features/academico/components/EmptyState';

export interface ColumnDef<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  rowKey: keyof T | ((row: T) => string);
  isLoading?: boolean;
  onSort?: (field: string) => void;
  sortField?: string;
  sortDirection?: 'asc' | 'desc';
  emptyMessage?: string;
}

export function DataTable<T extends object>({
  columns,
  data,
  rowKey,
  isLoading,
  onSort,
  sortField,
  sortDirection,
  emptyMessage = 'No hay datos disponibles',
}: DataTableProps<T>) {
  const [visibleColumns, setVisibleColumns] = useState<Set<string>>(
    new Set(columns.map((c) => c.key)),
  );

  const toggleColumn = (key: string) => {
    setVisibleColumns((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const visibleColDefs = columns.filter((c) => visibleColumns.has(c.key));

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return <EmptyState message={emptyMessage} icon="table_rows" />;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-end gap-2">
        <div className="relative">
          <button
            type="button"
            className="flex items-center gap-1 rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-1.5 text-label-sm text-on-surface-variant transition-colors hover:bg-surface-container-low"
            onClick={() => {
              const menu = document.getElementById('column-toggle-menu');
              if (menu) {
                menu.classList.toggle('hidden');
              }
            }}
          >
            <span className="material-symbols-outlined text-[16px]">view_column</span>
            Columnas
          </button>
          <div
            id="column-toggle-menu"
            className="absolute right-0 z-50 mt-1 hidden w-48 rounded-lg border border-outline-variant bg-surface-container-lowest p-2 shadow-lg"
          >
            {columns.map((col) => (
              <label
                key={col.key}
                className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-2.5 text-label-sm text-on-surface transition-colors hover:bg-surface-container-low min-h-[44px]"
              >
                <input
                  type="checkbox"
                  checked={visibleColumns.has(col.key)}
                  onChange={() => toggleColumn(col.key)}
                  className="h-4 w-4 rounded border-outline-variant bg-surface-container-low text-primary focus:ring-primary"
                />
                {col.label}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto rounded-xl border border-outline-variant">
        <table className="w-full text-left text-label-md">
          <thead>
            <tr className="border-b border-outline-variant bg-surface-container-low">
              {visibleColDefs.map((col) => (
                <th
                  key={col.key}
                  className={`px-4 py-3 font-medium text-on-surface ${
                    col.sortable ? 'cursor-pointer select-none hover:text-primary' : ''
                  }`}
                  onClick={() => {
                    if (col.sortable && onSort) {
                      onSort(col.key);
                    }
                  }}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {col.sortable && sortField === col.key && (
                      <span className="material-symbols-outlined text-[16px] text-primary">
                        {sortDirection === 'asc' ? 'arrow_upward' : 'arrow_downward'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => {
              const key = typeof rowKey === 'function' ? rowKey(row) : String(row[rowKey]);
              return (
                <tr
                  key={key}
                  className="border-b border-outline-variant transition-colors hover:bg-surface-container-low"
                >
                  {visibleColDefs.map((col) => (
                    <td key={col.key} className="px-4 py-3 text-on-surface-variant">
                      {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? '')}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
