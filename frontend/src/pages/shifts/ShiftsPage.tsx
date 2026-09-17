import { useEffect, useState } from "react";
import { shiftsApi, sitesApi } from "../../api/resources";
import type { Shift, Site } from "../../api/types";
import { CrudList } from "../../components/CrudList";
import { todayLocalISODate } from "../../utils/dates";
import { ShiftForm } from "./ShiftForm";

export function ShiftsPage() {
  const [shifts, setShifts] = useState<Shift[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Shift | "new" | null>(null);
  const [duplicateInitial, setDuplicateInitial] = useState<Partial<Shift> | null>(null);

  async function reload() {
    const [shiftList, siteList] = await Promise.all([shiftsApi.list(), sitesApi.list()]);
    setShifts(shiftList);
    setSites(siteList);
  }

  useEffect(() => {
    reload().finally(() => setLoading(false));
  }, []);

  async function handleDuplicateLast() {
    const last = await shiftsApi.latest();
    if (!last) return;
    setDuplicateInitial({
      site: last.site,
      date: todayLocalISODate(),
      start_time: last.start_time,
      end_time: last.end_time,
      hourly_rate: last.hourly_rate,
      shift_type: last.shift_type,
    });
    setEditing("new");
  }

  async function handleSubmit(values: Record<string, unknown>) {
    if (editing === "new") {
      await shiftsApi.create(values);
    } else if (editing) {
      await shiftsApi.update(editing.id, values);
    }
    setEditing(null);
    setDuplicateInitial(null);
    await reload();
  }

  async function handleDelete(shift: Shift) {
    if (!confirm(`Delete the shift on ${shift.date} at ${shift.site_name}?`)) return;
    await shiftsApi.remove(shift.id);
    await reload();
  }

  if (loading) return <p>Loading…</p>;

  if (editing) {
    const initial = editing === "new" ? duplicateInitial ?? {} : editing;
    return (
      <>
        <h1>{editing === "new" ? "Add shift" : "Edit shift"}</h1>
        <ShiftForm
          sites={sites}
          initial={initial}
          onSubmit={handleSubmit}
          onCancel={() => {
            setEditing(null);
            setDuplicateInitial(null);
          }}
        />
      </>
    );
  }

  return (
    <>
      <h1>Shifts</h1>
      <button type="button" className="btn" onClick={() => setEditing("new")}>
        + Add shift
      </button>{" "}
      {shifts.length > 0 && (
        <button type="button" className="btn secondary" onClick={handleDuplicateLast}>
          ⧉ Duplicate last shift
        </button>
      )}
      <CrudList
        items={shifts}
        emptyMessage="No shifts logged yet."
        onEdit={setEditing}
        onDelete={handleDelete}
        columns={[
          { header: "Date", render: (s) => s.date },
          { header: "Site", render: (s) => s.site_name },
          { header: "Agency", render: (s) => s.agency_name },
          { header: "Hours", render: (s) => s.duration_hours.toFixed(2) },
          { header: "Rate", render: (s) => `£${s.hourly_rate}/hr` },
          { header: "Pay", render: (s) => `£${s.calculated_pay.toFixed(2)}` },
        ]}
      />
    </>
  );
}
