import { useEffect, useState } from "react"
import { getHealth, getSessions, type Health, type Session } from "../api/client"

function confidenceBadge(confidence: number | null) {
  if (confidence == null) return <span className="text-slate-400">&mdash;</span>
  const pct = (confidence * 100).toFixed(0)
  let color: string
  let label: string
  if (confidence >= 0.7) {
    color = "bg-emerald-100 text-emerald-700"
    label = "High"
  } else if (confidence >= 0.4) {
    color = "bg-amber-100 text-amber-700"
    label = "Medium"
  } else {
    color = "bg-red-100 text-red-700"
    label = "Low"
  }
  return <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
    <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
    {label} ({pct}%)
  </span>
}

function statusBadge(status: string) {
  const colors: Record<string, string> = {
    open: "bg-blue-100 text-blue-700",
    closed: "bg-slate-100 text-slate-500",
  }
  return <span className={`inline-block px-2.5 py-0.5 rounded text-xs font-medium ${colors[status] || "bg-slate-100 text-slate-500"}`}>{status}</span>
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return "—"
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

function parseApps(activeApps: string): string {
  try {
    const apps = JSON.parse(activeApps || "[]")
    return Array.isArray(apps) ? apps.join(", ") : apps
  } catch {
    return activeApps || "—"
  }
}

export default function Sessions() {
  const [health, setHealth] = useState<Health | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  async function fetch() {
    try {
      const [h, s] = await Promise.all([getHealth(), getSessions()])
      setHealth(h)
      setSessions(s.sessions)
    } catch {
      if (!health) setHealth(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetch()
    const interval = setInterval(fetch, 30000)
    return () => clearInterval(interval)
  }, [])

  const agentOnline = health?.status === "ok"

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">Click a session to view details and inferred intent</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${agentOnline ? "bg-emerald-500" : "bg-red-400"}`}
              title={agentOnline ? "API reachable" : "API unreachable"} />
            <span className="text-sm text-slate-500">
              {loading ? "Checking..." : agentOnline ? `v${health?.version}` : "Offline"}
            </span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-sm text-slate-400">
          Loading sessions...
        </div>
      ) : sessions.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100 bg-slate-50">
            <p className="text-sm font-medium text-slate-600">No sessions recorded yet</p>
          </div>
          <div className="p-6 text-center text-sm text-slate-400">
            Start the capture agent to begin recording sessions.
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider">
                  <th className="text-left px-4 py-3 font-semibold">Status</th>
                  <th className="text-left px-4 py-3 font-semibold">Start</th>
                  <th className="text-left px-4 py-3 font-semibold">Duration</th>
                  <th className="text-center px-4 py-3 font-semibold">Events</th>
                  <th className="text-left px-4 py-3 font-semibold">Apps</th>
                  <th className="text-left px-4 py-3 font-semibold">Type</th>
                  <th className="text-left px-4 py-3 font-semibold">Goal</th>
                  <th className="text-left px-4 py-3 font-semibold">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-slate-50 transition-colors cursor-pointer"
                    onClick={() => window.location.hash = `#/sessions/${s.id}`}>
                    <td className="px-4 py-3">{statusBadge(s.status)}</td>
                    <td className="px-4 py-3 text-slate-600 whitespace-nowrap">
                      {new Date(s.start_time).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-slate-600 whitespace-nowrap">
                      {formatDuration(s.duration_seconds)}
                    </td>
                    <td className="px-4 py-3 text-slate-600 text-center">{s.event_count}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-[180px] truncate" title={parseApps(s.active_apps)}>
                      {parseApps(s.active_apps)}
                    </td>
                    <td className="px-4 py-3 text-slate-600 capitalize">{s.session_type || "—"}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-[200px] truncate" title={s.goal ?? undefined}>
                      {s.goal || "—"}
                    </td>
                    <td className="px-4 py-3">{confidenceBadge(s.confidence)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
