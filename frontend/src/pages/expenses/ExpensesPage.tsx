import { useEffect, useState } from "react";
import { agenciesApi, expensesApi } from "../../api/resources";
import type { Agency, Expense } from "../../api/types";
import { CrudList } from "../../components/CrudList";
import { CrudForm } from "../../components/CrudForm";
import type { FieldSpec } from "../../components/CrudForm";

const CATEGORY_LABELS: Record<string, string> = {
  UNIFORM: "Uniform",
  TRAVEL: "Travel",
  EQUIPMENT: "Equipment",
  OTHER: "Other",
};

export function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Expense | "new" | null>(null);

  async function reload() {
    const [expenseList, agencyList] = await Promise.all([expensesApi.list(), agenciesApi.list()]);
    setExpenses(expenseList);
    setAgencies(agencyList);
  }

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  const fields: FieldSpec[] = [
    { name: "date", label: "Date", kind: "date", required: true },
    {
      name: "category",
      label: "Category",
      kind: "select-string",
      required: true,
      options: Object.entries(CATEGORY_LABELS).map(([value, label]) => ({ value, label })),
    },
    { name: "amount", label: "Amount (£)", kind: "number", step: "0.01", required: true },
    {
      name: "agency",
      label: "Agency (optional)",
      kind: "select-number",
      placeholder: "No agency",
      options: agencies.map((a) => ({ value: a.id, label: a.name })),
    },
    { name: "notes", label: "Notes", kind: "textarea" },
  ];

  async function handleSubmit(values: Record<string, unknown>) {
    if (editing === "new") {
      await expensesApi.create(values);
    } else if (editing) {
      await expensesApi.update(editing.id, values);
    }
    setEditing(null);
    await reload();
  }

  async function handleDelete(expense: Expense) {
    if (!confirm(`Delete this ${CATEGORY_LABELS[expense.category]} expense of £${expense.amount}?`)) return;
    await expensesApi.remove(expense.id);
    await reload();
  }

  if (loading) return <p>Loading…</p>;

  if (editing) {
    return (
      <>
        <h1>{editing === "new" ? "Add expense" : "Edit expense"}</h1>
        <CrudForm
          fields={fields}
          initial={editing === "new" ? {} : editing}
          onSubmit={handleSubmit}
          onCancel={() => setEditing(null)}
        />
      </>
    );
  }

  return (
    <>
      <h1>Expenses</h1>
      <button type="button" className="btn" onClick={() => setEditing("new")}>
        + Add expense
      </button>
      <CrudList
        items={expenses}
        emptyMessage="No expenses logged yet."
        onEdit={setEditing}
        onDelete={handleDelete}
        columns={[
          { header: "Date", render: (e) => e.date },
          { header: "Category", render: (e) => CATEGORY_LABELS[e.category] },
          { header: "Amount", render: (e) => `£${e.amount}` },
          { header: "Agency", render: (e) => e.agency_name ?? "—" },
        ]}
      />
    </>
  );
}
