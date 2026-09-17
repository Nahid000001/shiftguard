import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardApi } from "../api/resources";
import type { DashboardSummary } from "../api/types";

export function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    dashboardApi.summary().then(setSummary);
  }, []);

  if (!summary) return <p>Loading…</p>;

  return (
    <>
      <h1>Dashboard</h1>

      <div className="stat-row">
        <div className="stat">
          <div className="value">£{summary.week_total.toFixed(2)}</div>
          <div className="label">
            This week's earnings ({formatShortDate(summary.week_start)} – {formatShortDate(summary.week_end)})
          </div>
        </div>
        <div className="stat">
          <div className="value">£{summary.month_total.toFixed(2)}</div>
          <div className="label">This month's earnings</div>
        </div>
        <div className="stat">
          <div className="value">{summary.upcoming_expiries.length}</div>
          <div className="label">Licences needing attention</div>
        </div>
      </div>

      <h2>This week's shifts</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Site</th>
            <th>Agency</th>
            <th>Hours</th>
            <th>Pay</th>
          </tr>
        </thead>
        <tbody>
          {summary.week_shifts.length === 0 && (
            <tr>
              <td colSpan={5}>
                No shifts logged this week yet. <Link to="/shifts">Log one</Link>.
              </td>
            </tr>
          )}
          {summary.week_shifts.map((shift) => (
            <tr key={shift.id}>
              <td>{formatDayDate(shift.date)}</td>
              <td>{shift.site_name}</td>
              <td>{shift.agency_name}</td>
              <td>{shift.duration_hours.toFixed(2)}</td>
              <td>£{shift.calculated_pay.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Licence expiries</h2>
      {summary.upcoming_expiries.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Licence</th>
              <th>Expiry</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {summary.upcoming_expiries.map((licence) => (
              <tr key={licence.id}>
                <td>{licence.name}</td>
                <td>{licence.expiry_date}</td>
                <td>
                  {licence.is_expired ? (
                    <span className="tag danger">Expired</span>
                  ) : (
                    <span className="tag warn">{licence.days_until_expiry} days left</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="card">
          No licences expiring in the next 30 days. <Link to="/licences">View all licences</Link>.
        </div>
      )}
    </>
  );
}

function formatShortDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
}

function formatDayDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-GB", { weekday: "short", day: "2-digit", month: "short" });
}
