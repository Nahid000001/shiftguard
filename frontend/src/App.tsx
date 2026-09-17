import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Landing } from "./pages/Landing";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { Dashboard } from "./pages/Dashboard";
import { Charts } from "./pages/Charts";
import { ShiftsPage } from "./pages/shifts/ShiftsPage";
import { AgenciesPage } from "./pages/agencies/AgenciesPage";
import { SitesPage } from "./pages/agencies/SitesPage";
import { LicencesPage } from "./pages/licences/LicencesPage";
import { ExpensesPage } from "./pages/expenses/ExpensesPage";
import { TaxSummary } from "./pages/TaxSummary";

/** Public marketing home for a signed-out visitor; signed-in users are sent
 * straight into the app instead of seeing "get started" copy every time. */
function HomeRoute() {
  const { username, loading } = useAuth();
  if (loading) return null;
  if (username) return <Navigate to="/dashboard" replace />;
  return <Landing />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomeRoute />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/charts" element={<Charts />} />
          <Route path="/shifts" element={<ShiftsPage />} />
          <Route path="/agencies" element={<AgenciesPage />} />
          <Route path="/sites" element={<SitesPage />} />
          <Route path="/licences" element={<LicencesPage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/tax-summary" element={<TaxSummary />} />
        </Route>
      </Route>
    </Routes>
  );
}
