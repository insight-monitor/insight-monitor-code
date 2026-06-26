import { useEffect, useState } from "react"
import { getSession, type SessionDetail as SessionDetailType, type RawEvent } from "./api/client"

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

function formatDuration(seconds: number | null): string {
  if (!seconds) return "—"
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = Math.floor(seconds % 60)
  if (h > 0) return `${h}h ${m}m`
  if (m > 0) return `${m}m ${s}s`
  return `${s}s`
}

function eventIcon(type: string) {
  switch (type) {
    case "window_focus": return "🪟"
    case "screenshot": return "📷"
    case "input_activity": return "⌨️"
    case "url_context": return "🌐"
    case "session_boundary": return "🔀"
    default: return "•"
  }
}

function EventTimeline({ events }: { events: RawEvent[] }) {
  return (
    <div className="space-y-1">
      {events.map((ev) => (
        <div key={ev.id || ev.event_id} className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0">
          <span className="text-lg mt-0.5">{eventIcon(ev.event_type)}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-500 uppercase">{ev.event_type.replace(/_/g, " ")}</span>
              <span className="text-xs text-gray-400">{new Date(ev.timestamp).toLocaleTimeString()}</span>
            </div>
            {ev.window_title && (
              <p className="text-sm text-gray-700 truncate mt-0.5" title={ev.window_title}>{ev.window_title}</p>
            )}
            {ev.process_name && (
              <p className="text-xs text-gray-500">{ev.process_name}</p>
            )}
            {ev.clicks_per_min != null && (
              <p className="text-xs text-gray-500">Clicks: {ev.clicks_per_min.toFixed(0)}/min · Keystrokes: {ev.keystrokes_per_min.toFixed(0)}/min</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function IntentCard({ intent }: { intent: NonNullable<SessionDetailType["intent"]> }) {
  return (
    <div className="bg-gradient-to-br from-purple-50 to-white border border-purple-200 rounded-lg p-5">
      <h3 className="text-sm font-semibold text-purple-800 uppercase tracking-wide mb-4">Inferred Intent</h3>

      <div className="space-y-4">
        <div>
          <p className="text-xs text-gray-500 mb-1">Session Type</p>
          <p className="text-sm font-medium text-gray-900 capitalize">{intent.session_type || "—"}</p>
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-1">Goal</p>
          <p className="text-sm text-gray-900">{intent.goal || "—"}</p>
          {intent.goal_confidence != null && (
            <div className="mt-1">{confidenceBadge(intent.goal_confidence)}</div>
          )}
        </div>

        {intent.friction_points.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-1">
              Friction Points
              {intent.friction_confidence != null && (
                <span className="ml-1">{confidenceBadge(intent.friction_confidence)}</span>
              )}
            </p>
            <ul className="space-y-1">
              {intent.friction_points.map((fp, i) => (
                <li key={i} className="flex items-start gap-1.5 text-sm text-gray-700">
                  <span className="text-red-400 mt-0.5">•</span>
                  {fp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {intent.tags.length > 0 && (
          <div>
            <p className="text-xs text-gray-500 mb-1.5">Tags</p>
            <div className="flex flex-wrap gap-1.5">
              {intent.tags.map((tag, i) => (
                <span key={i} className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div>
          <p className="text-xs text-gray-500 mb-1">Category</p>
          <p className="text-sm text-gray-900 capitalize">{intent.category}</p>
          {intent.category_confidence != null && (
            <div className="mt-1">{confidenceBadge(intent.category_confidence)}</div>
          )}
        </div>
      </div>
    </div>
  )
}

interface Props {
  sessionId: string
  onBack: () => void
}

export default function SessionDetail({ sessionId, onBack }: Props) {
  const [session, setSession] = useState<SessionDetailType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSession(sessionId)
      .then(setSession)
      .catch(() => setSession(null))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-sm text-gray-400">Loading session...</p>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 mb-4">Session not found</p>
          <button onClick={onBack} className="text-sm text-blue-600 hover:underline">← Back to sessions</button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button onClick={onBack} className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1">
              ← Back
            </button>
            <h1 className="text-lg font-bold text-gray-900">Session Detail</h1>
          </div>
          <span className="text-xs text-gray-400 font-mono">{session.id.slice(0, 8)}…</span>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Session summary */}
        <div className="bg-white rounded-lg border border-gray-200 p-5 mb-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Summary</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Status</p>
              <p className="font-medium capitalize mt-0.5">{session.status}</p>
            </div>
            <div>
              <p className="text-gray-500">Start</p>
              <p className="font-medium mt-0.5">{new Date(session.start_time).toLocaleString()}</p>
            </div>
            <div>
              <p className="text-gray-500">Duration</p>
              <p className="font-medium mt-0.5">{formatDuration(session.duration_seconds)}</p>
            </div>
            <div>
              <p className="text-gray-500">Events</p>
              <p className="font-medium mt-0.5">{session.event_count}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Timeline */}
          <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 p-5">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Timeline ({session.events.length} events)
            </h2>
            <EventTimeline events={session.events} />
          </div>

          {/* Intent card */}
          <div className="lg:col-span-1">
            {session.intent ? (
              <IntentCard intent={session.intent} />
            ) : (
              <div className="bg-gray-50 rounded-lg border border-gray-200 p-5 text-center">
                <p className="text-sm text-gray-500">No intent record yet</p>
                <p className="text-xs text-gray-400 mt-1">Close the session to trigger inference</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
