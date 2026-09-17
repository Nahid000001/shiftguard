import { useState } from "react";
import type { FormEvent } from "react";

export type FieldSpec =
  | { name: string; label: string; kind: "text" | "textarea"; required?: boolean }
  | { name: string; label: string; kind: "number"; required?: boolean; step?: string }
  | { name: string; label: string; kind: "date"; required?: boolean }
  | {
      name: string;
      label: string;
      kind: "select-number" | "select-string";
      required?: boolean;
      options: { value: string | number; label: string }[];
      placeholder?: string;
    };

interface CrudFormProps {
  fields: FieldSpec[];
  initial: object;
  onSubmit: (values: Record<string, unknown>) => Promise<void>;
  onCancel: () => void;
  submitLabel?: string;
}

function toInputValue(v: string | number | null | undefined): string {
  if (v === null || v === undefined) return "";
  return String(v);
}

export function CrudForm({ fields, initial, onSubmit, onCancel, submitLabel = "Save" }: CrudFormProps) {
  const initialRecord = initial as Record<string, string | number | null | undefined>;
  const [values, setValues] = useState<Record<string, string>>(() => {
    const initialState: Record<string, string> = {};
    for (const field of fields) {
      initialState[field.name] = toInputValue(initialRecord[field.name]);
    }
    return initialState;
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function setValue(name: string, value: string) {
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  function parseField(field: FieldSpec, raw: string): unknown {
    if (raw === "") {
      return field.required ? "" : null;
    }
    if (field.kind === "number" || field.kind === "select-number") {
      return Number(raw);
    }
    return raw;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const payload: Record<string, unknown> = {};
    for (const field of fields) {
      payload[field.name] = parseField(field, values[field.name] ?? "");
    }
    setSubmitting(true);
    try {
      await onSubmit(payload);
    } catch {
      setError("Couldn't save - check the fields and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p style={{ color: "var(--danger)", fontSize: "0.85rem" }}>{error}</p>}
      {fields.map((field) => (
        <div className="field" key={field.name}>
          <label htmlFor={field.name}>{field.label}</label>
          {field.kind === "textarea" ? (
            <textarea
              id={field.name}
              rows={3}
              value={values[field.name] ?? ""}
              onChange={(e) => setValue(field.name, e.target.value)}
              required={field.required}
            />
          ) : field.kind === "select-number" || field.kind === "select-string" ? (
            <select
              id={field.name}
              value={values[field.name] ?? ""}
              onChange={(e) => setValue(field.name, e.target.value)}
              required={field.required}
            >
              <option value="">{field.placeholder ?? "----------"}</option>
              {field.options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          ) : (
            <input
              id={field.name}
              type={field.kind === "date" ? "date" : field.kind === "number" ? "number" : "text"}
              step={field.kind === "number" ? field.step : undefined}
              value={values[field.name] ?? ""}
              onChange={(e) => setValue(field.name, e.target.value)}
              required={field.required}
            />
          )}
        </div>
      ))}
      <button type="submit" className="btn" disabled={submitting}>
        {submitting ? "Saving…" : submitLabel}
      </button>{" "}
      <button type="button" className="btn secondary" onClick={onCancel}>
        Cancel
      </button>
    </form>
  );
}
