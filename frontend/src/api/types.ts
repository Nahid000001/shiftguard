export type EmploymentType = "PAYE" | "SELF_EMPLOYED";

export interface Agency {
  id: number;
  name: string;
  employment_type: EmploymentType;
  contact_notes: string;
}

export interface Site {
  id: number;
  agency: number;
  agency_name: string;
  name: string;
  address: string;
  default_hourly_rate: string | null;
}

export type ShiftType = "STANDARD" | "OVERTIME" | "NIGHT" | "BANK_HOLIDAY";

export interface Shift {
  id: number;
  site: number;
  site_name: string;
  agency_name: string;
  date: string;
  start_time: string;
  end_time: string;
  hourly_rate: string;
  shift_type: ShiftType;
  notes: string;
  duration_hours: number;
  calculated_pay: number;
}

export interface Licence {
  id: number;
  name: string;
  licence_number: string;
  issue_date: string;
  expiry_date: string;
  reminder_days_before: number;
  days_until_expiry: number;
  is_expired: boolean;
  is_expiring_soon: boolean;
}

export type ExpenseCategory = "UNIFORM" | "TRAVEL" | "EQUIPMENT" | "OTHER";

export interface Expense {
  id: number;
  date: string;
  category: ExpenseCategory;
  amount: string;
  agency: number | null;
  agency_name: string | null;
  notes: string;
}

export interface DashboardSummary {
  week_start: string;
  week_end: string;
  week_shifts: Shift[];
  week_total: number;
  month_total: number;
  upcoming_expiries: Licence[];
}

export interface ChartCategoryPoint {
  name: string;
  value: number;
  color_index: number;
}

export interface ChartsData {
  trend: { label: string; total: number }[];
  hours_by_agency: ChartCategoryPoint[];
  pay_by_site: ChartCategoryPoint[];
  has_data: boolean;
}

export interface TaxQuarterRow {
  label: string;
  start: string;
  end: string;
  is_future: boolean;
  paye_income: number;
  self_employed_income: number;
  expenses_total: number;
  self_employed_expenses: number;
  self_employed_net: number;
}

export interface TaxSummary {
  start_year: number;
  label: string;
  rows: TaxQuarterRow[];
  totals: Omit<TaxQuarterRow, "label" | "start" | "end" | "is_future">;
  ytd: {
    self_employed_income: number;
    expenses_total: number;
    self_employed_net: number;
  };
  prev_year: number;
  prev_label: string;
  next_year: number;
  next_label: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
