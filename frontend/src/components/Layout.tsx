import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const navLinks = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/charts", label: "Charts" },
  { to: "/shifts", label: "Shifts" },
  { to: "/agencies", label: "Agencies" },
  { to: "/sites", label: "Sites" },
  { to: "/licences", label: "Licences" },
  { to: "/expenses", label: "Expenses" },
  { to: "/tax-summary", label: "Tax summary" },
];

export function Layout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <>
      <nav>
        <NavLink to="/dashboard" className="brand">
          ShiftGuard
        </NavLink>
        {navLinks.map(({ to, label }) => (
          <NavLink key={to} to={to} className={({ isActive }) => (isActive ? "active" : "")}>
            {label}
          </NavLink>
        ))}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleLogout();
          }}
          style={{ marginLeft: "auto" }}
        >
          <button type="submit" className="btn secondary" style={{ width: "auto" }}>
            Sign out
          </button>
        </form>
      </nav>
      <main>
        <Outlet />
      </main>
    </>
  );
}
