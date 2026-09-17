import { api, fetchAllPages } from "./client";
import type {
  Agency,
  ChartsData,
  DashboardSummary,
  Expense,
  Licence,
  Shift,
  Site,
  TaxSummary,
} from "./types";

export const agenciesApi = {
  list: () => fetchAllPages<Agency>("/api/agencies/"),
  create: (data: Partial<Agency>) => api.post<Agency>("/api/agencies/", data),
  update: (id: number, data: Partial<Agency>) => api.put<Agency>(`/api/agencies/${id}/`, data),
  remove: (id: number) => api.delete(`/api/agencies/${id}/`),
};

export const sitesApi = {
  list: () => fetchAllPages<Site>("/api/sites/"),
  create: (data: Partial<Site>) => api.post<Site>("/api/sites/", data),
  update: (id: number, data: Partial<Site>) => api.put<Site>(`/api/sites/${id}/`, data),
  remove: (id: number) => api.delete(`/api/sites/${id}/`),
};

export const shiftsApi = {
  list: () => fetchAllPages<Shift>("/api/shifts/"),
  /** The API's default ordering (see Shift.Meta.ordering) is already
   * most-recent-first, so the first page's first result is the latest shift. */
  latest: async (): Promise<Shift | null> => {
    const page = await api.get<{ results: Shift[] }>("/api/shifts/");
    return page.results[0] ?? null;
  },
  create: (data: Partial<Shift>) => api.post<Shift>("/api/shifts/", data),
  update: (id: number, data: Partial<Shift>) => api.put<Shift>(`/api/shifts/${id}/`, data),
  remove: (id: number) => api.delete(`/api/shifts/${id}/`),
};

export const licencesApi = {
  list: () => fetchAllPages<Licence>("/api/licences/"),
  create: (data: Partial<Licence>) => api.post<Licence>("/api/licences/", data),
  update: (id: number, data: Partial<Licence>) => api.put<Licence>(`/api/licences/${id}/`, data),
  remove: (id: number) => api.delete(`/api/licences/${id}/`),
};

export const expensesApi = {
  list: () => fetchAllPages<Expense>("/api/expenses/"),
  create: (data: Partial<Expense>) => api.post<Expense>("/api/expenses/", data),
  update: (id: number, data: Partial<Expense>) => api.put<Expense>(`/api/expenses/${id}/`, data),
  remove: (id: number) => api.delete(`/api/expenses/${id}/`),
};

export const dashboardApi = {
  summary: () => api.get<DashboardSummary>("/api/dashboard/summary/"),
  charts: () => api.get<ChartsData>("/api/dashboard/charts/"),
};

export const reportsApi = {
  taxSummary: (year?: number) =>
    api.get<TaxSummary>(`/api/reports/tax-summary/${year ? `?year=${year}` : ""}`),
};
