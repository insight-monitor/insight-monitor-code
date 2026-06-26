import { useEffect, useState } from "react"
import { getHealth, getSessions, type Health, type Session } from "./api/client"

function confidenceBadge(confidence: number | null) {
  if (confidence == null) return <span className="text-gray-400">—</span>

  const pct = (confidence * 100).toFixed(0)
  let color: string
  let label: string

  if (confidence >= 0.7) {
    color = "bg-green-100 text-green-800"
    label = "High"
  } else if (confidence >= 0.4) {
    color = "bg-yellow-100 text-yellow-800"
    label = "Medium"
  } else {
    color = "bg-red-100 text-red-800"
    label = "Low"
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${color}`}>
      <span className="w-1.5 h-1.5 rounded-full currentColor opacity-60" />
      {label} ({pct}%)
    </span>
  )
}

function statusBadge(status: string) {
  const colors: Record<string, string> = {
    open: "bg-blue-100 text-blue-800",
    closed: "bg-gray-100 text-gray-600",
  }
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[status] || "bg-gray-100"}`}>
      {status}
    </span>
  )
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

function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetch() {
      try {
        const [h, s] = await Promise.all([
          getHealth(),
          getSessions(),
        ])
        setHealth(h)
        setSessions(s.sessions)
      } catch {
        setHealth(null)
      } finally {
        setLoading(false)
      }
    }
    fetch()
    const interval = setInterval(fetch, 10000)
    return () => clearInterval(interval)
  }, [])

  const agentOnline = health?.status === "ok"

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Insight Monitor</h1>
          <div className="flex items-center gap-2">
            <span
              className={`w-2.5 h-2.5 rounded-full ${agentOnline ? "bg-green-500" : "bg-red-400"}`}
              title={agentOnline ? "API reachable" : "API unreachable"}
            />
            <span className="text-sm text-gray-500">
              {loading ? "Checking..." : agentOnline ? `v${health?.version}` : "Offline"}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900">Sessions</h2>
          <p className="text-gray-500 mt-1">Monitor your computer activity sessions</p>
        </div>

        {loading ? (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400 text-sm">
            Loading sessions...
          </div>
        ) : sessions.length === 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
              <p className="text-sm font-medium text-gray-700">No sessions recorded yet</p>
            </div>
            <div className="p-6 text-center text-gray-400 text-sm">
              Start the capture agent to begin recording sessions.
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Start</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Duration</th>
                    <th className="text-center px-4 py-3 font-medium text-gray-600">Events</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Apps</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Goal</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {sessions.map((s) => (
                    <tr key={s.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3">{statusBadge(s.status)}</td>
                      <td className="px-4 py-3 text-gray-700 whitespace-nowrap">
                        {new Date(s.start_time).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-gray-700 whitespace-nowrap">
                        {formatDuration(s.duration_seconds)}
                      </td>
                      <td className="px-4 py-3 text-gray-700 text-center">{s.event_count}</td>
                      <td className="px-4 py-3 text-gray-700 max-w-[180px] truncate" title={parseApps(s.active_apps)}>
                        {parseApps(s.active_apps)}
                      </td>
                      <td className="px-4 py-3 text-gray-700 capitalize">{s.session_type || "—"}</td>
                      <td className="px-4 py-3 text-gray-700 max-w-[200px] truncate" title={s.goal ?? undefined}>
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
      </main>
    </div>
  )
}

export default App
