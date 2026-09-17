import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
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

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
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
