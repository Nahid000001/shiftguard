import { useEffect, useState } from "react";
import { licencesApi } from "../../api/resources";
import type { Licence } from "../../api/types";
import { CrudList } from "../../components/CrudList";
import { CrudForm } from "../../components/CrudForm";
import type { FieldSpec } from "../../components/CrudForm";

const fields: FieldSpec[] = [
  { name: "name", label: "Name", kind: "text", required: true },
  { name: "licence_number", label: "Licence number", kind: "text", required: true },
  { name: "issue_date", label: "Issue date", kind: "date", required: true },
  { name: "expiry_date", label: "Expiry date", kind: "date", required: true },
  { name: "reminder_days_before", label: "Reminder days before expiry", kind: "number" },
];

function StatusTag({ licence }: { licence: Licence }) {
  if (licence.is_expired) return <span className="tag danger">Expired</span>;
  if (licence.is_expiring_soon) {
    return <span className="tag warn">Expires in {licence.days_until_expiry} days</span>;
  }
  return <span className="tag good">Valid</span>;
}

export function LicencesPage() {
  const [licences, setLicences] = useState<Licence[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Licence | "new" | null>(null);

  async function reload() {
    setLicences(await licencesApi.list());
  }

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  async function handleSubmit(values: Record<string, unknown>) {
    if (editing === "new") {
      await licencesApi.create(values);
    } else if (editing) {
      await licencesApi.update(editing.id, values);
    }
    setEditing(null);
    await reload();
  }

  async function handleDelete(licence: Licence) {
    if (!confirm(`Delete "${licence.name}"?`)) return;
    await licencesApi.remove(licence.id);
    await reload();
  }

  if (loading) return <p>Loading…</p>;

  if (editing) {
    return (
      <>
        <h1>{editing === "new" ? "Add licence" : "Edit licence"}</h1>
        <CrudForm
          fields={fields}
          initial={
            editing === "new"
              ? { reminder_days_before: 60 }
              : editing
          }
          onSubmit={handleSubmit}
          onCancel={() => setEditing(null)}
        />
      </>
    );
  }

  return (
    <>
      <h1>Licences</h1>
      <button type="button" className="btn" onClick={() => setEditing("new")}>
        + Add licence
      </button>
      <CrudList
        items={licences}
        emptyMessage="No licences yet."
        onEdit={setEditing}
        onDelete={handleDelete}
        columns={[
          { header: "Name", render: (l) => l.name },
          { header: "Number", render: (l) => l.licence_number },
          { header: "Expiry", render: (l) => l.expiry_date },
          { header: "Status", render: (l) => <StatusTag licence={l} /> },
        ]}
      />
    </>
  );
}
