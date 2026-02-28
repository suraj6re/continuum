export default function Table({ columns, data, className = '' }) {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full">
        <thead className="bg-bg-section border-b border-border-warm">
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className="px-4 py-3 text-left text-xs font-semibold text-text-secondary uppercase tracking-wider">
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-warm">
          {data.map((row, rowIdx) => (
            <tr key={rowIdx} className="hover:bg-bg-section transition-colors">
              {columns.map((col, colIdx) => (
                <td key={colIdx} className="px-4 py-3 text-sm text-text-primary">
                  {col.render ? col.render(row) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
