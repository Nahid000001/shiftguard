import { useState } from "react";

interface PasswordInputProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete?: string;
  required?: boolean;
}

export function PasswordInput({ id, value, onChange, autoComplete, required }: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div style={{ position: "relative" }}>
      <input
        id={id}
        type={visible ? "text" : "password"}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete={autoComplete}
        required={required}
        style={{ paddingRight: "3.2rem" }}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        style={{
          position: "absolute",
          right: "0.4rem",
          top: "0.4rem",
          background: "none",
          border: "none",
          color: "var(--muted)",
          fontSize: "0.75rem",
          fontWeight: 600,
          cursor: "pointer",
          padding: "0.3rem 0.5rem",
        }}
      >
        {visible ? "Hide" : "Show"}
      </button>
    </div>
  );
}
