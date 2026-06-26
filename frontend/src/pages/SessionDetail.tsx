import { useEffect, useState } from "react"
import { getSession, type SessionDetail as SessionDetailType, type RawEvent } from "../api/client"

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
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-60" />
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
  const icons: Record<string, string> = {
    window_focus: "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z",
    screenshot: "M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z",
    input_activity: "M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z",
    url_context: "M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9",
    session_boundary: "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4",
  }
  return icons[type] || "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
}

function eventBg(type: string) {
  const colors: Record<string, string> = {
    window_focus: "bg-sky-100 text-sky-600",
    screenshot: "bg-pink-100 text-pink-600",
    input_activity: "bg-emerald-100 text-emerald-600",
    url_context: "bg-purple-100 text-purple-600",
    session_boundary: "bg-amber-100 text-amber-600",
  }
  return colors[type] || "bg-slate-100 text-slate-500"
}

function EventTimeline({ events }: { events: RawEvent[] }) {
  return (
    <div className="space-y-1">
      {events.map((ev) => (
        <div key={ev.id || ev.event_id} className="flex items-start gap-3 py-2.5 border-b border-slate-100 last:border-0">
          <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${eventBg(ev.event_type)}`}>
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={eventIcon(ev.event_type)} />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{ev.event_type.replace(/_/g, " ")}</span>
              <span className="text-xs text-slate-400">{new Date(ev.timestamp).toLocaleTimeString()}</span>
            </div>
            {ev.window_title && (
              <p className="text-sm text-slate-700 truncate mt-0.5" title={ev.window_title}>{ev.window_title}</p>
            )}
            {ev.process_name && (
              <p className="text-xs text-slate-500">{ev.process_name}</p>
            )}
            {ev.clicks_per_min != null && ev.keystrokes_per_min != null && (
              <p className="text-xs text-slate-500">Clicks: {ev.clicks_per_min.toFixed(0)}/min &middot; Keystrokes: {ev.keystrokes_per_min.toFixed(0)}/min</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function IntentCard({ intent }: { intent: NonNullable<SessionDetailType["intent"]> }) {
  return (
    <div className="bg-gradient-to-br from-purple-50 to-white border border-purple-200 rounded-xl p-5">
      <h3 className="text-sm font-bold text-purple-800 uppercase tracking-wide mb-4 flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        Inferred Intent
      </h3>

      <div className="space-y-4">
        <div>
          <p className="text-xs text-slate-500 mb-0.5">Session Type</p>
          <p className="text-sm font-medium text-slate-900 capitalize">{intent.session_type || "—"}</p>
        </div>

        <div>
          <p className="text-xs text-slate-500 mb-0.5">Goal</p>
          <p className="text-sm text-slate-900">{intent.goal || "—"}</p>
          {intent.goal_confidence != null && <div className="mt-1">{confidenceBadge(intent.goal_confidence)}</div>}
        </div>

        {intent.friction_points.length > 0 && (
          <div>
            <p className="text-xs text-slate-500 mb-1">
              Friction Points
              {intent.friction_confidence != null && <span className="ml-1">{confidenceBadge(intent.friction_confidence)}</span>}
            </p>
            <ul className="space-y-1">
              {intent.friction_points.map((fp, i) => (
                <li key={i} className="flex items-start gap-1.5 text-sm text-slate-700">
                  <span className="text-red-400 mt-0.5">&bull;</span>
                  {fp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {intent.tags.length > 0 && (
          <div>
            <p className="text-xs text-slate-500 mb-1">Tags</p>
            <div className="flex flex-wrap gap-1.5">
              {intent.tags.map((tag, i) => (
                <span key={i} className="px-2.5 py-0.5 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div>
          <p className="text-xs text-slate-500 mb-0.5">Category</p>
          <p className="text-sm text-slate-900 capitalize">{intent.category}</p>
          {intent.category_confidence != null && <div className="mt-1">{confidenceBadge(intent.category_confidence)}</div>}
        </div>
      </div>
    </div>
  )
}

export default function SessionDetail({ sessionId }: { sessionId: string }) {
  const [session, setSession] = useState<SessionDetailType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSession(sessionId)
      .then(setSession)
      .catch(() => setSession(null))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (loading) {
    return <div className="flex justify-center py-10"><div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full" /></div>
  }

  if (!session) {
    return (
      <div className="text-center py-10">
        <p className="text-slate-500 mb-4">Session not found</p>
        <a href="#/sessions" className="text-sm text-blue-600 hover:underline no-underline">← Back to sessions</a>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <a href="#/sessions" className="text-sm text-slate-500 hover:text-slate-700 flex items-center gap-1 no-underline">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </a>
        <span className="text-xs text-slate-400 font-mono">{session.id.slice(0, 8)}&hellip;</span>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wide mb-4">Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-slate-500 text-xs">Status</p>
            <p className="font-medium capitalize mt-0.5 text-slate-900">{session.status}</p>
          </div>
          <div>
            <p className="text-slate-500 text-xs">Start</p>
            <p className="font-medium mt-0.5 text-slate-900">{new Date(session.start_time).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-slate-500 text-xs">Duration</p>
            <p className="font-medium mt-0.5 text-slate-900">{formatDuration(session.duration_seconds)}</p>
          </div>
          <div>
            <p className="text-slate-500 text-xs">Events</p>
            <p className="font-medium mt-0.5 text-slate-900">{session.event_count}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wide mb-4">
            Timeline ({session.events.length} events)
          </h3>
          <EventTimeline events={session.events} />
        </div>

        <div className="lg:col-span-1">
          {session.intent ? (
            <IntentCard intent={session.intent} />
          ) : (
            <div className="bg-slate-50 rounded-xl border border-slate-200 p-6 text-center">
              <p className="text-sm text-slate-500">No intent record yet</p>
              <p className="text-xs text-slate-400 mt-1">Close the session to trigger inference</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
