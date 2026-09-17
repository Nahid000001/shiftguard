import type { ReactNode } from "react";

export interface Column<T> {
  header: string;
  render: (item: T) => ReactNode;
}

interface CrudListProps<T extends { id: number }> {
  items: T[];
  columns: Column<T>[];
  onEdit: (item: T) => void;
  onDelete: (item: T) => void;
  emptyMessage: string;
}

export function CrudList<T extends { id: number }>({
  items,
  columns,
  onEdit,
  onDelete,
  emptyMessage,
}: CrudListProps<T>) {
  return (
    <table>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.header}>{col.header}</th>
          ))}
          <th />
        </tr>
      </thead>
      <tbody>
        {items.length === 0 && (
          <tr>
            <td colSpan={columns.length + 1}>{emptyMessage}</td>
          </tr>
        )}
        {items.map((item) => (
          <tr key={item.id}>
            {columns.map((col) => (
              <td key={col.header}>{col.render(item)}</td>
            ))}
            <td className="row-actions">
              <button type="button" onClick={() => onEdit(item)}>
                Edit
              </button>
              <button type="button" onClick={() => onDelete(item)}>
                Delete
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
