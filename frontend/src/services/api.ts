const BASE = "/api";

async function get<T>(path: string, params?: Record<string, string | number>): Promise<T | null> {
  try {
    const url = new URL(BASE + path, window.location.origin);
    if (params) {
      Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));
    }
    const res = await fetch(url.toString());
    if (!res.ok) return null;
    return res.json() as Promise<T>;
  } catch {
    return null;
  }
}

// ── Types ────────────────────────────────────────────────────────────────────

export interface Metrics {
  timestamp: number;
  cpu_pct: number;
  ram_pct: number;
  rps_pct: number;
  rps_actual: number;
  replicas: number;
}

export interface Status {
  replicas: number;
  max_replicas: number;
  service_name: string;
  last_alert: {
    level: string;
    message: string;
    timestamp: number | null;
  };
  last_decision: {
    delta_replicas: number;
    delta_raw: number;
    alert_level: string;
    alert_score: number;
    timestamp: number;
  } | null;
}

export interface HistoryPoint {
  timestamp: number;
  cpu_pct: number;
  ram_pct: number;
  rps_pct: number;
  rps_actual: number;
  replicas: number;
}

export interface ContainerStat {
  id: string;
  name: string;
  cpu_pct: number;
  ram_pct: number;
  ram_mb: number;
}

export interface Decision {
  timestamp: number;
  cpu_pct: number;
  ram_pct: number;
  rps_pct: number;
  delta_replicas: number;
  delta_raw: number;
  alert_score: number;
  alert_level: string;
}

export interface Alert {
  timestamp: number;
  level: string;
  message: string;
}

export interface HttpStats {
  "2xx": number;
  "4xx": number;
  "5xx": number;
  total: number;
}

export interface HostInfo {
  ram_total_gb: number;
  cpu_count: number;
}

// ── Fetch functions ──────────────────────────────────────────────────────────

export const fetchMetrics    = ()           => get<Metrics>("/metrics");
export const fetchStatus     = ()           => get<Status>("/status");
export const fetchHistory    = (limit = 120) => get<HistoryPoint[]>("/history",  { limit });
export const fetchContainers = ()           => get<ContainerStat[]>("/containers");
export const fetchDecisions  = (limit = 20) => get<Decision[]>("/decisions",   { limit });
export const fetchAlerts     = (limit = 20) => get<Alert[]>("/alerts",         { limit });
export const fetchHttpStats  = ()           => get<HttpStats>("/http-stats");
export const fetchHostInfo   = ()           => get<HostInfo>("/host-info");
