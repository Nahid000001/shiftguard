import { useEffect, useState } from "react";
import { agenciesApi } from "../../api/resources";
import type { Agency } from "../../api/types";
import { CrudList } from "../../components/CrudList";
import { CrudForm } from "../../components/CrudForm";
import type { FieldSpec } from "../../components/CrudForm";

const fields: FieldSpec[] = [
  { name: "name", label: "Name", kind: "text", required: true },
  {
    name: "employment_type",
    label: "Employment type",
    kind: "select-string",
    required: true,
    options: [
      { value: "PAYE", label: "PAYE" },
      { value: "SELF_EMPLOYED", label: "Self-employed" },
    ],
  },
  { name: "contact_notes", label: "Contact notes", kind: "textarea" },
];

export function AgenciesPage() {
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Agency | "new" | null>(null);

  async function reload() {
    setAgencies(await agenciesApi.list());
  }

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  async function handleSubmit(values: Record<string, unknown>) {
    if (editing === "new") {
      await agenciesApi.create(values);
    } else if (editing) {
      await agenciesApi.update(editing.id, values);
    }
    setEditing(null);
    await reload();
  }

  async function handleDelete(agency: Agency) {
    if (!confirm(`Delete "${agency.name}"? This will also delete its sites and their shifts.`)) return;
    await agenciesApi.remove(agency.id);
    await reload();
  }

  if (loading) return <p>Loading…</p>;

  if (editing) {
    return (
      <>
        <h1>{editing === "new" ? "Add agency" : "Edit agency"}</h1>
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
      <h1>Agencies</h1>
      <button type="button" className="btn" onClick={() => setEditing("new")}>
        + Add agency
      </button>
      <CrudList
        items={agencies}
        emptyMessage="No agencies yet."
        onEdit={setEditing}
        onDelete={handleDelete}
        columns={[
          { header: "Name", render: (a) => a.name },
          {
            header: "Type",
            render: (a) => (a.employment_type === "PAYE" ? "PAYE" : "Self-employed"),
          },
        ]}
      />
    </>
  );
}
