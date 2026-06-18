interface LoadingStateProps {
  rows?: number;
  cols?: number;
}

export function LoadingState({ rows = 4, cols = 5 }: LoadingStateProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-outline-variant">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-outline-variant bg-surface-container-low">
            {Array.from({ length: cols }).map((_, i) => (
              <th key={i} className="px-4 py-3">
                <div className="h-4 w-20 animate-pulse rounded bg-surface-container-low" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, row) => (
            <tr key={row} className="border-b border-outline-variant">
              {Array.from({ length: cols }).map((_, col) => (
                <td key={col} className="px-4 py-3">
                  <div className="h-4 w-full animate-pulse rounded bg-surface-container-low" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
