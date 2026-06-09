import { useState, useEffect, useCallback } from "react";
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  fetchMetrics, fetchStatus, fetchHistory,
  fetchContainers, fetchDecisions, fetchAlerts, fetchHttpStats, fetchHostInfo,
  type Metrics, type Status, type HistoryPoint,
  type ContainerStat, type Decision, type Alert, type HttpStats, type HostInfo,
} from "../services/api";

// ── Helpers ──────────────────────────────────────────────────────────────────

function fmtTime(ts: number) {
  return new Date(ts * 1000).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}

function timeAgo(ts: number) {
  const diff = Math.floor(Date.now() / 1000 - ts);
  if (diff < 60) return "agora";
  if (diff < 3600) return `há ${Math.floor(diff / 60)} min`;
  return `há ${Math.floor(diff / 3600)} h`;
}

function metricLevel(pct: number): "ok" | "warn" | "crit" {
  if (pct < 55) return "ok";
  if (pct < 80) return "warn";
  return "crit";
}

function deltaLabel(delta: number) {
  if (delta > 0) return "subir";
  if (delta < 0) return "derrubar";
  return "manter";
}

// ── Micro components ─────────────────────────────────────────────────────────

const LEVEL_COLORS: Record<string, string> = {
  ok:   "#0F6E56",
  warn: "#BA7517",
  crit: "#A32D2D",
  base: "#1a1a1a",
};

function MetricCard({ label, value, sub, level = "base" }: {
  label: string; value: string | number; sub?: string; level?: string;
}) {
  return (
    <div style={{ background: "#f5f5f3", borderRadius: 8, padding: "12px 14px", flex: 1, minWidth: 0 }}>
      <div style={{ fontSize: 11, color: "#888", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 500, color: LEVEL_COLORS[level] ?? LEVEL_COLORS.base, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: "#888", marginTop: 3 }}>{sub}</div>}
    </div>
  );
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ fontSize: 11, fontWeight: 500, color: "#888", textTransform: "uppercase", letterSpacing: "0.05em", margin: "20px 0 8px" }}>
      {children}
    </div>
  );
}

function Card({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{ background: "#fff", border: "0.5px solid #e0e0de", borderRadius: 8, padding: "12px 14px", ...style }}>
      {children}
    </div>
  );
}

function CardTitle({ children }: { children: React.ReactNode }) {
  return <div style={{ fontSize: 12, fontWeight: 500, color: "#888", marginBottom: 10 }}>{children}</div>;
}

function MiniBar({ pct, color }: { pct: number; color: string }) {
  return (
    <div style={{ background: "#f0f0ee", borderRadius: 99, height: 4, overflow: "hidden", marginBottom: 3 }}>
      <div style={{ width: `${Math.min(pct, 100)}%`, background: color, height: "100%", borderRadius: 99 }} />
    </div>
  );
}

function DecisionBadge({ label }: { label: string }) {
  const styles: Record<string, React.CSSProperties> = {
    subir:    { background: "#E1F5EE", color: "#085041" },
    derrubar: { background: "#FCEBEB", color: "#791F1F" },
    manter:   { background: "#f0f0ee", color: "#666" },
  };
  return (
    <span style={{ fontSize: 11, padding: "2px 8px", borderRadius: 99, whiteSpace: "nowrap", ...(styles[label] ?? styles.manter) }}>
      {label}
    </span>
  );
}

function AlertDot({ level }: { level: string }) {
  const colors: Record<string, string> = { warning: "#BA7517", critical: "#A32D2D", ok: "#1D9E75" };
  return (
    <div style={{ width: 7, height: 7, borderRadius: "50%", background: colors[level] ?? "#888", marginTop: 5, flexShrink: 0 }} />
  );
}

const LEGEND = [["#378ADD", "cpu"], ["#7F77DD", "ram"], ["#1D9E75", "rps"]];

// ── Main component ────────────────────────────────────────────────────────────

export default function HelmsmanDashboard() {
  const [metrics,    setMetrics]    = useState<Metrics | null>(null);
  const [status,     setStatus]     = useState<Status | null>(null);
  const [history,    setHistory]    = useState<HistoryPoint[]>([]);
  const [containers, setContainers] = useState<ContainerStat[]>([]);
  const [decisions,  setDecisions]  = useState<Decision[]>([]);
  const [alerts,     setAlerts]     = useState<Alert[]>([]);
  const [httpStats,  setHttpStats]  = useState<HttpStats | null>(null);
  const [hostInfo,   setHostInfo]   = useState<HostInfo | null>(null);

  const refresh = useCallback(async () => {
    const [m, s, h, c, d, a, hs, hi] = await Promise.all([
      fetchMetrics(),
      fetchStatus(),
      fetchHistory(120),
      fetchContainers(),
      fetchDecisions(20),
      fetchAlerts(20),
      fetchHttpStats(),
      fetchHostInfo(),
    ]);
    if (m)  setMetrics(m);
    if (s)  setStatus(s);
    if (h)  setHistory(h);
    if (c)  setContainers(c);
    if (d)  setDecisions(d);
    if (a)  setAlerts(a);
    if (hs) setHttpStats(hs);
    if (hi) setHostInfo(hi);
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 3000);
    return () => clearInterval(id);
  }, [refresh]);

  const cpu      = metrics?.cpu_pct    ?? 0;
  const ram      = metrics?.ram_pct    ?? 0;
  const rps      = metrics?.rps_actual ?? 0;
  const rpsPct   = metrics?.rps_pct    ?? 0;
  const replicas    = status?.replicas     ?? 0;
  const maxReplicas = status?.max_replicas ?? 6;
  const serviceName = status?.service_name ?? null;
  const ramGb       = hostInfo?.ram_total_gb ?? null;
  const cpuCount    = hostInfo?.cpu_count    ?? null;

  const lastDec = status?.last_decision;
  const decValue = lastDec
    ? `${lastDec.delta_replicas >= 0 ? "+" : ""}${lastDec.delta_replicas} réplica${Math.abs(lastDec.delta_replicas) !== 1 ? "s" : ""}`
    : "—";
  const decSub = lastDec ? `${timeAgo(lastDec.timestamp)} · ${deltaLabel(lastDec.delta_replicas)}` : undefined;

  const chartData = history.map(p => ({
    time: fmtTime(p.timestamp),
    cpu:      Math.round(p.cpu_pct),
    ram:      Math.round(p.ram_pct),
    rps:      Math.round(p.rps_pct),
    replicas: p.replicas,
    rps_abs:  Math.round(p.rps_actual),
  }));

  const httpRows = httpStats && httpStats.total > 0
    ? [
        { label: "2xx", pct: httpStats["2xx"], color: "#1D9E75" },
        { label: "4xx", pct: httpStats["4xx"], color: "#EF9F27" },
        { label: "5xx", pct: httpStats["5xx"], color: "#E24B4A" },
      ]
    : null;

  const live = metrics !== null;

  return (
    <div style={{ background: "#f8f8f6", minHeight: "100vh", padding: 16, fontFamily: "system-ui, sans-serif" }}>

      {/* topbar */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 15, fontWeight: 500 }}>
            <span style={{ color: "#378ADD" }}>⬡</span> Helmsman
            {serviceName && <span style={{ color: "#aaa", fontWeight: 400 }}> · {serviceName}</span>}
          </span>
          <span style={{ width: 7, height: 7, borderRadius: "50%", background: live ? "#1D9E75" : "#ccc", display: "inline-block" }} />
          <span style={{ fontSize: 11, color: live ? "#1D9E75" : "#aaa" }}>{live ? "live" : "aguardando..."}</span>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          {[
            `${replicas} réplica${replicas !== 1 ? "s" : ""}`,
            ramGb    ? `host: ${ramGb} GB · ${cpuCount} vCPUs` : "polling 3s",
          ].map(t => (
            <span key={t} style={{ fontSize: 11, padding: "3px 10px", borderRadius: 99, background: "#f0f0ee", color: "#666", border: "0.5px solid #e0e0de" }}>{t}</span>
          ))}
        </div>
      </div>

      {/* visão geral */}
      <SectionLabel>visão geral do host</SectionLabel>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <MetricCard label="cpu do host"    value={`${cpu.toFixed(1)}%`}  sub={cpuCount ? `${(cpu / 100 * cpuCount).toFixed(1)} / ${cpuCount} vCPUs` : undefined} level={metricLevel(cpu)} />
        <MetricCard label="ram do host"    value={`${ram.toFixed(1)}%`}  sub={ramGb    ? `${(ram / 100 * ramGb).toFixed(1)} / ${ramGb} GB`              : undefined} level={metricLevel(ram)} />
        <MetricCard label="rps atual"      value={Math.round(rps)}       sub={`${rpsPct.toFixed(0)}% da capacidade`}       level={metricLevel(rpsPct)} />
        <MetricCard label="última decisão" value={decValue}              sub={decSub} level="base" />
      </div>

      {/* containers */}
      <SectionLabel>containers ativos</SectionLabel>
      <Card style={{ marginBottom: 12 }}>
        {containers.length === 0 ? (
          <div style={{ fontSize: 12, color: "#aaa", padding: "8px 0" }}>nenhum container ativo</div>
        ) : (
          <>
            <div style={{ display: "flex", gap: 4, marginBottom: 8 }}>
              {["nome", "cpu · ram", "valores"].map((h, i) => (
                <div key={h} style={{ flex: i === 1 ? 2 : i === 0 ? 1 : 0, minWidth: i === 2 ? 64 : 0, fontSize: 10, color: "#888", textAlign: i === 2 ? "right" : "left" }}>{h}</div>
              ))}
            </div>
            {containers.map((c, i) => {
              const warn = c.cpu_pct > 80 || c.ram_pct > 80;
              return (
                <div key={c.id} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 0", borderBottom: i < containers.length - 1 ? "0.5px solid #f0f0ee" : "none" }}>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: warn ? "#EF9F27" : "#1D9E75", flexShrink: 0 }} />
                  <div style={{ flex: 1, fontSize: 12, fontFamily: "monospace" }}>{c.name}</div>
                  <div style={{ flex: 2 }}>
                    <MiniBar pct={c.cpu_pct} color="#378ADD" />
                    <MiniBar pct={c.ram_pct} color="#7F77DD" />
                  </div>
                  <div style={{ fontSize: 10, color: "#888", textAlign: "right", minWidth: 64, lineHeight: 1.6 }}>
                    {c.cpu_pct.toFixed(1)}% cpu<br />{c.ram_pct.toFixed(1)}% ram
                  </div>
                </div>
              );
            })}
            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              {[["#378ADD", "cpu"], ["#7F77DD", "ram"]].map(([color, label]) => (
                <span key={label} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, color: "#888" }}>
                  <span style={{ width: 10, height: 3, background: color, display: "inline-block", borderRadius: 2 }} />{label}
                </span>
              ))}
            </div>
          </>
        )}
      </Card>

      {/* análise temporal */}
      <SectionLabel>análise temporal — últimas 2 horas</SectionLabel>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
        <Card>
          <CardTitle>cpu · ram · rps (%)</CardTitle>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0ee" />
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#aaa" }} interval={Math.floor(chartData.length / 6)} />
              <YAxis tick={{ fontSize: 9, fill: "#aaa" }} domain={[0, 100]} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: "0.5px solid #e0e0de" }} />
              <Line type="monotone" dataKey="cpu" stroke="#378ADD" strokeWidth={1.5} dot={false} name="cpu %" />
              <Line type="monotone" dataKey="ram" stroke="#7F77DD" strokeWidth={1.5} dot={false} strokeDasharray="4 2" name="ram %" />
              <Line type="monotone" dataKey="rps" stroke="#1D9E75" strokeWidth={1.5} dot={false} strokeDasharray="2 2" name="rps %" />
            </LineChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", gap: 12, marginTop: 4 }}>
            {LEGEND.map(([c, l]) => (
              <span key={l} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 10, color: "#888" }}>
                <span style={{ width: 10, height: 2, background: c, display: "inline-block" }} />{l}
              </span>
            ))}
          </div>
        </Card>

        <Card>
          <CardTitle>réplicas ativas</CardTitle>
          <ResponsiveContainer width="100%" height={140}>
            <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0ee" />
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#aaa" }} interval={Math.floor(chartData.length / 6)} />
              <YAxis tick={{ fontSize: 9, fill: "#aaa" }} domain={[0, maxReplicas + 1]} allowDecimals={false} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: "0.5px solid #e0e0de" }} />
              <Area type="stepAfter" dataKey="replicas" stroke="#378ADD" fill="#E6F1FB" strokeWidth={2} dot={false} name="réplicas" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* requests */}
      <SectionLabel>requests</SectionLabel>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 12 }}>
        <Card>
          <CardTitle>req/s — últimas 2 horas</CardTitle>
          <ResponsiveContainer width="100%" height={140}>
            <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0ee" />
              <XAxis dataKey="time" tick={{ fontSize: 9, fill: "#aaa" }} interval={Math.floor(chartData.length / 6)} />
              <YAxis tick={{ fontSize: 9, fill: "#aaa" }} />
              <Tooltip contentStyle={{ fontSize: 11, borderRadius: 6, border: "0.5px solid #e0e0de" }} />
              <Area type="monotone" dataKey="rps_abs" stroke="#1D9E75" fill="#E1F5EE" strokeWidth={1.5} dot={false} name="req/s" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <CardTitle>distribuição de status http — últimos 5 min</CardTitle>
          {httpRows ? (
            <div style={{ marginTop: 12 }}>
              {httpRows.map(({ label, pct, color }) => (
                <div key={label} style={{ marginBottom: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "#888", marginBottom: 3 }}>
                    <span>{label}</span><span>{pct}%</span>
                  </div>
                  <div style={{ background: "#f0f0ee", borderRadius: 99, height: 6, overflow: "hidden" }}>
                    <div style={{ width: `${pct}%`, background: color, height: "100%", borderRadius: 99 }} />
                  </div>
                </div>
              ))}
              <div style={{ fontSize: 10, color: "#aaa", marginTop: 6 }}>{httpStats?.total ?? 0} req neste período</div>
            </div>
          ) : (
            <div style={{ fontSize: 12, color: "#aaa", marginTop: 12 }}>sem dados de tráfego ainda</div>
          )}
        </Card>
      </div>

      {/* decisões fuzzy */}
      <SectionLabel>decisões fuzzy recentes</SectionLabel>
      <Card style={{ marginBottom: 12 }}>
        {decisions.length === 0 ? (
          <div style={{ fontSize: 12, color: "#aaa", padding: "8px 0" }}>nenhuma decisão ainda</div>
        ) : decisions.map((d, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 0", borderBottom: i < decisions.length - 1 ? "0.5px solid #f0f0ee" : "none" }}>
            <span style={{ fontSize: 10, color: "#aaa", minWidth: 36 }}>{fmtTime(d.timestamp)}</span>
            <DecisionBadge label={deltaLabel(d.delta_replicas)} />
            <span style={{ fontSize: 10, color: "#888", flex: 1 }}>
              cpu {d.cpu_pct.toFixed(0)}% · ram {d.ram_pct.toFixed(0)}% · rps {d.rps_pct.toFixed(0)}%
              {" "}→ delta {d.delta_replicas >= 0 ? "+" : ""}{d.delta_replicas}
            </span>
            <span style={{ fontSize: 10, color: "#aaa" }}>{d.alert_level}</span>
          </div>
        ))}
      </Card>

      {/* alertas */}
      <SectionLabel>alertas</SectionLabel>
      <Card>
        {alerts.length === 0 ? (
          <div style={{ fontSize: 12, color: "#aaa", padding: "8px 0" }}>nenhum alerta</div>
        ) : alerts.slice().reverse().map((a, i) => (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, padding: "7px 0", borderBottom: i < alerts.length - 1 ? "0.5px solid #f0f0ee" : "none" }}>
            <AlertDot level={a.level} />
            <div>
              <div style={{ fontSize: 12, color: "#1a1a1a", lineHeight: 1.4 }}>{a.message}</div>
              <div style={{ fontSize: 10, color: "#aaa", marginTop: 2 }}>
                {fmtTime(a.timestamp)} · {a.level}
              </div>
            </div>
          </div>
        ))}
      </Card>

    </div>
  );
}
