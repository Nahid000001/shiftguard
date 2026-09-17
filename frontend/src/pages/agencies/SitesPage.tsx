import { useEffect, useState } from "react";
import { agenciesApi, sitesApi } from "../../api/resources";
import type { Agency, Site } from "../../api/types";
import { CrudList } from "../../components/CrudList";
import { CrudForm } from "../../components/CrudForm";
import type { FieldSpec } from "../../components/CrudForm";

export function SitesPage() {
  const [sites, setSites] = useState<Site[]>([]);
  const [agencies, setAgencies] = useState<Agency[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Site | "new" | null>(null);

  async function reload() {
    const [siteList, agencyList] = await Promise.all([sitesApi.list(), agenciesApi.list()]);
    setSites(siteList);
    setAgencies(agencyList);
  }

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  const fields: FieldSpec[] = [
    {
      name: "agency",
      label: "Agency",
      kind: "select-number",
      required: true,
      options: agencies.map((a) => ({ value: a.id, label: a.name })),
    },
    { name: "name", label: "Site name", kind: "text", required: true },
    { name: "address", label: "Address", kind: "text" },
    { name: "default_hourly_rate", label: "Default hourly rate (£)", kind: "number", step: "0.01" },
  ];

  async function handleSubmit(values: Record<string, unknown>) {
    if (editing === "new") {
      await sitesApi.create(values);
    } else if (editing) {
      await sitesApi.update(editing.id, values);
    }
    setEditing(null);
    await reload();
  }

  async function handleDelete(site: Site) {
    if (!confirm(`Delete "${site.name}"? This will also delete its shifts.`)) return;
    await sitesApi.remove(site.id);
    await reload();
  }

  if (loading) return <p>Loading…</p>;

  if (editing) {
    return (
      <>
        <h1>{editing === "new" ? "Add site" : "Edit site"}</h1>
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
      <h1>Sites</h1>
      <button type="button" className="btn" onClick={() => setEditing("new")}>
        + Add site
      </button>
      <CrudList
        items={sites}
        emptyMessage="No sites yet."
        onEdit={setEditing}
        onDelete={handleDelete}
        columns={[
          { header: "Name", render: (s) => s.name },
          { header: "Agency", render: (s) => s.agency_name },
          {
            header: "Default rate",
            render: (s) => (s.default_hourly_rate ? `£${s.default_hourly_rate}/hr` : "—"),
          },
        ]}
      />
    </>
  );
}
