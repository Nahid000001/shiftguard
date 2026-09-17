import { useState } from "react";
import type { FormEvent } from "react";
import type { Shift, ShiftType, Site } from "../../api/types";

const SHIFT_TYPES: { value: ShiftType; label: string }[] = [
  { value: "STANDARD", label: "Standard" },
  { value: "OVERTIME", label: "Overtime" },
  { value: "NIGHT", label: "Night" },
  { value: "BANK_HOLIDAY", label: "Bank holiday" },
];

interface ShiftFormValues {
  site: string;
  date: string;
  start_time: string;
  end_time: string;
  hourly_rate: string;
  shift_type: ShiftType;
  notes: string;
}

interface ShiftFormProps {
  sites: Site[];
  initial: Partial<Shift>;
  onSubmit: (values: Record<string, unknown>) => Promise<void>;
  onCancel: () => void;
}

export function ShiftForm({ sites, initial, onSubmit, onCancel }: ShiftFormProps) {
  const [values, setValues] = useState<ShiftFormValues>({
    site: initial.site ? String(initial.site) : "",
    date: initial.date ?? "",
    start_time: initial.start_time?.slice(0, 5) ?? "",
    end_time: initial.end_time?.slice(0, 5) ?? "",
    hourly_rate: initial.hourly_rate ?? "",
    shift_type: initial.shift_type ?? "STANDARD",
    notes: initial.notes ?? "",
  });
  // Tracks whether hourly_rate currently holds a value we auto-filled (rather
  // than one the user typed), so picking a different site can still refresh
  // it - but only until the user actually edits the field themselves.
  const [rateAutofilled, setRateAutofilled] = useState(!initial.hourly_rate);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set<K extends keyof ShiftFormValues>(key: K, value: ShiftFormValues[K]) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  function handleSiteChange(siteId: string) {
    set("site", siteId);
    if (!rateAutofilled && values.hourly_rate !== "") return;
    const site = sites.find((s) => String(s.id) === siteId);
    if (site?.default_hourly_rate) {
      set("hourly_rate", site.default_hourly_rate);
      setRateAutofilled(true);
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({
        site: Number(values.site),
        date: values.date,
        start_time: values.start_time,
        end_time: values.end_time,
        hourly_rate: values.hourly_rate,
        shift_type: values.shift_type,
        notes: values.notes,
      });
    } catch {
      setError("Couldn't save - check the fields and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p style={{ color: "var(--danger)", fontSize: "0.85rem" }}>{error}</p>}
      <div className="field">
        <label htmlFor="site">Site</label>
        <select id="site" value={values.site} onChange={(e) => handleSiteChange(e.target.value)} required>
          <option value="">----------</option>
          {sites.map((site) => (
            <option key={site.id} value={site.id}>
              {site.name} ({site.agency_name})
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="date">Date</label>
        <input id="date" type="date" value={values.date} onChange={(e) => set("date", e.target.value)} required />
      </div>
      <div className="field">
        <label htmlFor="start_time">Start time</label>
        <input
          id="start_time"
          type="time"
          value={values.start_time}
          onChange={(e) => set("start_time", e.target.value)}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="end_time">End time</label>
        <input
          id="end_time"
          type="time"
          value={values.end_time}
          onChange={(e) => set("end_time", e.target.value)}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="hourly_rate">Hourly rate (£)</label>
        <input
          id="hourly_rate"
          type="number"
          step="0.01"
          value={values.hourly_rate}
          onChange={(e) => {
            set("hourly_rate", e.target.value);
            setRateAutofilled(false);
          }}
          required
        />
      </div>
      <div className="field">
        <label htmlFor="shift_type">Shift type</label>
        <select
          id="shift_type"
          value={values.shift_type}
          onChange={(e) => set("shift_type", e.target.value as ShiftType)}
        >
          {SHIFT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>
      <div className="field">
        <label htmlFor="notes">Notes</label>
        <textarea id="notes" rows={2} value={values.notes} onChange={(e) => set("notes", e.target.value)} />
      </div>
      <button type="submit" className="btn" disabled={submitting}>
        {submitting ? "Saving…" : "Save"}
      </button>{" "}
      <button type="button" className="btn secondary" onClick={onCancel}>
        Cancel
      </button>
    </form>
  );
}
