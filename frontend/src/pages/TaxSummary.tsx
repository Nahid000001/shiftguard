import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { API_BASE } from "../api/client";
import { reportsApi } from "../api/resources";
import type { TaxSummary as TaxSummaryData } from "../api/types";

export function TaxSummary() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [summary, setSummary] = useState<TaxSummaryData | null>(null);

  const yearParam = searchParams.get("year");
  const year = yearParam ? Number(yearParam) : undefined;

  useEffect(() => {
    reportsApi.taxSummary(year).then(setSummary);
  }, [year]);

  if (!summary) return <p>Loading…</p>;

  return (
    <>
      <h1>Tax summary — {summary.label}</h1>

      <div className="row-actions" style={{ marginBottom: "1rem" }}>
        <a href="#" onClick={(e) => { e.preventDefault(); setSearchParams({ year: String(summary.prev_year) }); }}>
          « {summary.prev_label}
        </a>
        <a href="#" onClick={(e) => { e.preventDefault(); setSearchParams({ year: String(summary.next_year) }); }}>
          {summary.next_label} »
        </a>{" "}
        <a
          className="btn secondary"
          href={`${API_BASE}/reports/tax-summary/export.csv?year=${summary.start_year}`}
        >
          Export CSV
        </a>{" "}
        <a
          className="btn secondary"
          href={`${API_BASE}/reports/tax-summary/export.pdf?year=${summary.start_year}`}
        >
          Export PDF
        </a>
      </div>

      <div className="stat-row">
        <div className="stat">
          <div className="value">£{summary.ytd.self_employed_income.toFixed(2)}</div>
          <div className="label">YTD self-employed income</div>
        </div>
        <div className="stat">
          <div className="value">£{summary.ytd.expenses_total.toFixed(2)}</div>
          <div className="label">YTD expenses</div>
        </div>
        <div className="stat">
          <div className="value">£{summary.ytd.self_employed_net.toFixed(2)}</div>
          <div className="label">YTD self-employed net</div>
        </div>
      </div>

      <table>
        <thead>
          <tr>
            <th>Quarter</th>
            <th>PAYE income</th>
            <th>Self-employed income</th>
            <th>Self-employed expenses</th>
            <th>Self-employed net</th>
          </tr>
        </thead>
        <tbody>
          {summary.rows.map((row) => (
            <tr key={row.label} style={row.is_future ? { opacity: 0.5 } : undefined}>
              <td>{row.label}</td>
              <td>£{row.paye_income.toFixed(2)}</td>
              <td>£{row.self_employed_income.toFixed(2)}</td>
              <td>£{row.self_employed_expenses.toFixed(2)}</td>
              <td>£{row.self_employed_net.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th>Tax year total</th>
            <th>£{summary.totals.paye_income.toFixed(2)}</th>
            <th>£{summary.totals.self_employed_income.toFixed(2)}</th>
            <th>£{summary.totals.self_employed_expenses.toFixed(2)}</th>
            <th>£{summary.totals.self_employed_net.toFixed(2)}</th>
          </tr>
        </tfoot>
      </table>
    </>
  );
}
