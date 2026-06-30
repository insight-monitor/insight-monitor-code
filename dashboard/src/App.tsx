import { useEffect, useState } from "react"
import { getHealth, getSessions, getSession, type Health, type Session, type SessionDetail, type RawEvent } from "./api/client"

function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSession, setSelectedSession] = useState<SessionDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [eventsOffset, setEventsOffset] = useState(0)
  const EVENTS_PER_PAGE = 20

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

  async function openSession(id: string) {
    setDetailLoading(true)
    setEventsOffset(0)
    try {
      const detail = await getSession(id, EVENTS_PER_PAGE, 0)
      setSelectedSession(detail)
    } catch {
      setSelectedSession(null)
    } finally {
      setDetailLoading(false)
    }
  }

  async function loadMoreEvents() {
    if (!selectedSession) return
    const newOffset = eventsOffset + EVENTS_PER_PAGE
    setEventsOffset(newOffset)
    try {
      const detail = await getSession(selectedSession.id, EVENTS_PER_PAGE, newOffset)
      setSelectedSession(prev => {
        if (!prev) return detail
        return { ...detail, events: [...prev.events, ...detail.events] }
      })
    } catch {
      setEventsOffset(prev => prev - EVENTS_PER_PAGE)
    }
  }

  function closeDetail() {
    setSelectedSession(null)
    setEventsOffset(0)
  }

  const agentOnline = health?.agent?.status === "online"
  const totalEvents = selectedSession?.event_count_total ?? selectedSession?.events?.length ?? 0
  const hasMore = selectedSession ? eventsOffset + EVENTS_PER_PAGE < totalEvents : false

  function formatDuration(seconds: number | null): string {
    if (!seconds) return "—"
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    if (h > 0) return `${h}h ${m}m`
    if (m > 0) return `${m}m ${s}s`
    return `${s}s`
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

  function eventIcon(type: string) {
    switch (type) {
      case "window_focus": return "🖥️"
      case "screenshot": return "📸"
      case "input_activity": return "⌨️"
      default: return "📋"
    }
  }

  function formatEvent(event: RawEvent) {
    const time = new Date(event.timestamp).toLocaleTimeString()
    switch (event.event_type) {
      case "window_focus":
        return `${time} — ${event.window_title || "unknown"} (${event.process_name || "?"})`
      case "screenshot":
        return `${time} — Screenshot captured`
      case "input_activity":
        return `${time} — Input: ${event.clicks_per_min ?? 0} clicks/min, ${event.keystrokes_per_min ?? 0} keys/min`
      default:
        return `${time} — ${event.event_type}`
    }
  }

  if (selectedSession) {
    const s = selectedSession
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={closeDetail}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                ← Back to Sessions
              </button>
              <h1 className="text-xl font-bold text-gray-900">Session Detail</h1>
              {statusBadge(s.status)}
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-xs text-gray-500 uppercase">Start Time</p>
              <p className="text-sm font-medium text-gray-900">{new Date(s.start_time).toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-xs text-gray-500 uppercase">Duration</p>
              <p className="text-sm font-medium text-gray-900">{formatDuration(s.duration_seconds)}</p>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <p className="text-xs text-gray-500 uppercase">Events</p>
              <p className="text-sm font-medium text-gray-900">{totalEvents}</p>
            </div>
          </div>

          {s.intent && (
            <div className="bg-white rounded-lg border border-gray-200 p-4 mb-8">
              <h3 className="text-sm font-semibold text-gray-900 mb-2">Inferred Intent</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Type:</span>{" "}
                  <span className="font-medium">{s.intent.session_type || "—"}</span>
                </div>
                <div>
                  <span className="text-gray-500">Goal:</span>{" "}
                  <span className="font-medium">{s.intent.goal || "—"}</span>
                </div>
                <div>
                  <span className="text-gray-500">Confidence:</span>{" "}
                  <span className="font-medium">{s.intent.goal_confidence != null ? `${(s.intent.goal_confidence * 100).toFixed(0)}%` : "—"}</span>
                </div>
                <div>
                  <span className="text-gray-500">Category:</span>{" "}
                  <span className="font-medium">{s.intent.category || "—"}</span>
                </div>
                {s.intent.tags.length > 0 && (
                  <div className="col-span-2">
                    <span className="text-gray-500">Tags:</span>{" "}
                    {s.intent.tags.map(tag => (
                      <span key={tag} className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-0.5 rounded mr-1">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-900">Event Timeline</h3>
              <span className="text-xs text-gray-500">
                Showing {s.events.length} of {totalEvents} events
              </span>
            </div>
            <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto">
              {s.events.map(event => (
                <div key={event.event_id} className="px-6 py-3 hover:bg-gray-50 flex items-start gap-3">
                  <span className="text-lg flex-shrink-0">{eventIcon(event.event_type)}</span>
                  <span className="text-sm text-gray-700">{formatEvent(event)}</span>
                </div>
              ))}
            </div>
            {hasMore && (
              <div className="px-6 py-3 border-t border-gray-100 bg-gray-50 text-center">
                <button
                  onClick={loadMoreEvents}
                  disabled={detailLoading}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium disabled:text-gray-400"
                >
                  {detailLoading ? "Loading..." : "Load More"}
                </button>
              </div>
            )}
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Insight Monitor</h1>
          <div className="flex items-center gap-3">
            <span
              className={`w-3 h-3 rounded-full ${agentOnline ? "bg-green-500" : "bg-red-400"}`}
              title={agentOnline ? "Agent Online" : "Agent Offline"}
            />
            <span className="text-sm text-gray-500">
                {loading ? "Checking..." : agentOnline ? `Capture Agent: Online v${health?.agent?.version}` : "Capture Agent: Offline"}
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
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Start</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Duration</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Events</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Apps</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Goal</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {sessions.map((s) => (
                  <tr key={s.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => openSession(s.id)}>
                    <td className="px-4 py-3">{statusBadge(s.status)}</td>
                    <td className="px-4 py-3 text-gray-700">
                      {new Date(s.start_time).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {formatDuration(s.duration_seconds)}
                    </td>
                    <td className="px-4 py-3 text-gray-700">{s.event_count}</td>
                    <td className="px-4 py-3 text-gray-700 max-w-[200px] truncate">
                      {(() => {
                        try {
                          const apps = JSON.parse(s.active_apps || "[]")
                          return apps.join(", ") || "—"
                        } catch {
                          return s.active_apps || "—"
                        }
                      })()}
                    </td>
                    <td className="px-4 py-3 text-gray-700">{s.session_type || "—"}</td>
                    <td className="px-4 py-3 text-gray-700 max-w-[200px] truncate" title={s.goal || undefined}>{s.goal || "—"}</td>
                    <td className="px-4 py-3 text-gray-700">{s.confidence != null ? `${(s.confidence * 100).toFixed(0)}%` : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
