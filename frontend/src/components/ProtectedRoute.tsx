import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function ProtectedRoute() {
  const { username, loading } = useAuth();

  if (loading) return null;
  if (!username) return <Navigate to="/login" replace />;
  return <Outlet />;
}
