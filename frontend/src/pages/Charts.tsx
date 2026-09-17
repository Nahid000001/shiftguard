import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Link } from "react-router-dom";
import { dashboardApi } from "../api/resources";
import type { ChartsData } from "../api/types";

const SERIES_COLORS = [
  "#3987e5",
  "#d95926",
  "#199e70",
  "#c98500",
  "#d55181",
  "#008300",
  "#9085e9",
  "#e66767",
];
const GRID_COLOR = "#2c2c2a";
const MUTED_COLOR = "#94a3b8";
const SURFACE = "#1e293b";

function ChartTooltip({
  active,
  payload,
  label,
  prefix = "",
}: {
  active?: boolean;
  payload?: { value: number }[];
  label?: string;
  prefix?: string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div
      style={{
        background: SURFACE,
        border: "1px solid #334155",
        borderRadius: 6,
        padding: "0.5rem 0.75rem",
        color: "#e2e8f0",
        fontSize: "0.85rem",
      }}
    >
      <div style={{ color: MUTED_COLOR }}>{label}</div>
      <div>
        {prefix}
        {payload[0].value.toFixed(2)}
      </div>
    </div>
  );
}

export function Charts() {
  const [data, setData] = useState<ChartsData | null>(null);

  useEffect(() => {
    dashboardApi.charts().then(setData);
  }, []);

  if (!data) return <p>Loading…</p>;

  if (!data.has_data) {
    return (
      <>
        <h1>Charts</h1>
        <div className="card">
          No shifts logged yet — charts will appear once you have some data. <Link to="/shifts">Log a shift</Link>.
        </div>
      </>
    );
  }

  return (
    <>
      <h1>Charts</h1>

      <div className="chart-card">
        <h2>Earnings trend (last 6 months)</h2>
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data.trend}>
              <CartesianGrid stroke={GRID_COLOR} vertical={false} />
              <XAxis dataKey="label" stroke={MUTED_COLOR} tick={{ fill: MUTED_COLOR, fontSize: 12 }} />
              <YAxis
                stroke={MUTED_COLOR}
                tick={{ fill: MUTED_COLOR, fontSize: 12 }}
                tickFormatter={(v) => `£${v}`}
              />
              <Tooltip content={<ChartTooltip prefix="£" />} />
              <Line
                type="monotone"
                dataKey="total"
                stroke={SERIES_COLORS[0]}
                strokeWidth={2}
                dot={{ r: 4, fill: SERIES_COLORS[0], stroke: SURFACE, strokeWidth: 2 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <details className="data-table">
          <summary>View as table</summary>
          <table>
            <thead>
              <tr>
                <th>Month</th>
                <th>Earnings</th>
              </tr>
            </thead>
            <tbody>
              {data.trend.map((row) => (
                <tr key={row.label}>
                  <td>{row.label}</td>
                  <td>£{row.total.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      </div>

      <CategoryChart title="Hours by agency (all time)" unit="" unitSuffix=" hrs" points={data.hours_by_agency} />
      <CategoryChart title="Pay by site (all time)" unit="£" unitSuffix="" points={data.pay_by_site} />
    </>
  );
}

function CategoryChart({
  title,
  points,
  unit,
  unitSuffix,
}: {
  title: string;
  points: ChartsData["hours_by_agency"];
  unit: string;
  unitSuffix: string;
}) {
  return (
    <div className="chart-card">
      <h2>{title}</h2>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={points}>
            <CartesianGrid stroke={GRID_COLOR} vertical={false} />
            <XAxis dataKey="name" stroke={MUTED_COLOR} tick={{ fill: MUTED_COLOR, fontSize: 12 }} />
            <YAxis
              stroke={MUTED_COLOR}
              tick={{ fill: MUTED_COLOR, fontSize: 12 }}
              tickFormatter={(v) => `${unit}${v}`}
            />
            <Tooltip content={<ChartTooltip prefix={unit} />} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={24}>
              {points.map((point) => (
                <Cell key={point.name} fill={SERIES_COLORS[point.color_index % SERIES_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <details className="data-table">
        <summary>View as table</summary>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            {points.map((point) => (
              <tr key={point.name}>
                <td>{point.name}</td>
                <td>
                  {unit}
                  {point.value.toFixed(2)}
                  {unitSuffix}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </div>
  );
}
