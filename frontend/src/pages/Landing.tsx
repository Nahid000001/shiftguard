import { Link } from "react-router-dom";

const PROBLEMS = [
  "Shifts scattered across multiple agencies, with no single view of your week or month",
  "Pay that varies by agency, site, and shift type — easy to be underpaid without noticing",
  "SIA licence expiry is a hard legal deadline: miss it and you can't legally work",
  "Sole traders need clean hours and income records for HMRC self-assessment",
];

const FEATURES = [
  {
    title: "One dashboard",
    body: "This week's shifts, this month's earnings, and upcoming licence expiries at a glance — across every agency you work for.",
  },
  {
    title: "Fast shift logging",
    body: "Log a shift in seconds. Duplicate your last one for repeat patterns, and site default rates fill in the hourly rate for you.",
  },
  {
    title: "Licence expiry tracking",
    body: "Your SIA licences show a clear warning once they're inside your reminder window, so renewal is never a surprise.",
  },
  {
    title: "Tax-ready reporting",
    body: "PAYE and self-employed income split by UK tax quarter, with expense tracking and CSV/PDF export for self-assessment.",
  },
  {
    title: "Charts that make sense",
    body: "Earnings trend, hours by agency, and pay by site — enough to spot patterns without wading through spreadsheets.",
  },
  {
    title: "Sign in your way",
    body: "Register with a username and password, or continue with Google — your choice.",
  },
];

export function Landing() {
  return (
    <div style={{ minHeight: "100vh" }}>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "1.25rem 1.5rem",
          maxWidth: "1100px",
          margin: "0 auto",
        }}
      >
        <span style={{ fontWeight: 700, color: "var(--accent)", fontSize: "1.1rem" }}>ShiftGuard</span>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <Link to="/login" className="btn secondary">
            Sign in
          </Link>
          <Link to="/register" className="btn">
            Get started
          </Link>
        </div>
      </header>

      <main style={{ maxWidth: "1100px", margin: "0 auto", padding: "2rem 1.5rem 4rem" }}>
        <section style={{ textAlign: "center", padding: "2.5rem 0 3rem" }}>
          <h1 style={{ fontSize: "2.2rem", lineHeight: 1.2, margin: "0 0 1rem" }}>
            One place to track shifts, pay, and licences —<br /> across every agency you work for
          </h1>
          <p style={{ color: "var(--muted)", fontSize: "1.05rem", maxWidth: "560px", margin: "0 auto 1.75rem" }}>
            Built for security contractors juggling multiple agencies, PAYE and self-employed income,
            and SIA licences that have to stay valid.
          </p>
          <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center" }}>
            <Link to="/register" className="btn" style={{ fontSize: "0.95rem", padding: "0.6rem 1.3rem" }}>
              Create a free account
            </Link>
            <Link to="/login" className="btn secondary" style={{ fontSize: "0.95rem", padding: "0.6rem 1.3rem" }}>
              Sign in
            </Link>
          </div>
        </section>

        <section className="card" style={{ padding: "1.75rem" }}>
          <h2 style={{ margin: "0 0 1rem", color: "var(--text)", fontSize: "1.1rem" }}>
            The problem with juggling multiple agencies
          </h2>
          <ul style={{ margin: 0, paddingLeft: "1.2rem", color: "var(--muted)", lineHeight: 1.8 }}>
            {PROBLEMS.map((p) => (
              <li key={p}>{p}</li>
            ))}
          </ul>
        </section>

        <section style={{ marginTop: "2.5rem" }}>
          <h2 style={{ textAlign: "center", fontSize: "1.3rem", margin: "0 0 1.5rem" }}>What ShiftGuard does</h2>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: "1rem",
            }}
          >
            {FEATURES.map((f) => (
              <div className="card" key={f.title} style={{ margin: 0 }}>
                <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem", color: "var(--accent)" }}>{f.title}</h3>
                <p style={{ margin: 0, color: "var(--muted)", fontSize: "0.9rem", lineHeight: 1.5 }}>{f.body}</p>
              </div>
            ))}
          </div>
        </section>

        <section style={{ textAlign: "center", marginTop: "3rem" }}>
          <Link to="/register" className="btn" style={{ fontSize: "0.95rem", padding: "0.6rem 1.3rem" }}>
            Get started — it's free
          </Link>
        </section>
      </main>

      <footer style={{ textAlign: "center", padding: "1.5rem", color: "var(--muted)", fontSize: "0.8rem" }}>
        ShiftGuard — a personal project for tracking security work across multiple agencies.
      </footer>
    </div>
  );
}
