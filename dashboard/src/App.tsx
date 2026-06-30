import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Activity, ArrowLeft, Monitor, ChevronDown, Sparkles } from "lucide-react"
import { getHealth, getSessions, getSession, type Health, type Session, type SessionDetail } from "./api/client"

const confidenceColor = (c: number | null) => {
  if (c == null) return "text-white/40"
  if (c >= 0.8) return "text-[#1d9e75]"
  if (c >= 0.5) return "text-[#ef9f27]"
  return "text-[#d85a30]"
}

const bgConfidence = (c: number | null) => {
  if (c == null) return ""
  if (c >= 0.8) return "bg-[#1d9e75]/10 text-[#1d9e75] border-[#1d9e75]/20"
  if (c >= 0.5) return "bg-[#ef9f27]/10 text-[#ef9f27] border-[#ef9f27]/20"
  return "bg-[#d85a30]/10 text-[#d85a30] border-[#d85a30]/20"
}

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
      open: "border-[#1d9e75]/30 text-[#1d9e75] bg-[#1d9e75]/8",
      closed: "border-white/10 text-white/50 bg-white/[0.03]",
    }
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11px] font-medium uppercase tracking-wider ${colors[status] || "border-white/10 text-white/50"}`}>
        {status === "open" && <span className="h-1.5 w-1.5 rounded-full bg-[#1d9e75]" />}
        {status}
      </span>
    )
  }

  function eventTypeMeta(type: string) {
    switch (type) {
      case "window_focus": return { icon: Monitor, label: "Window Focus" }
      case "screenshot": return { icon: Activity, label: "Screenshot" }
      case "input_activity": return { icon: Activity, label: "Input" }
      default: return { icon: Activity, label: type }
    }
  }

  if (selectedSession) {
    const s = selectedSession
    return (
      <div className="min-h-screen">
        <header className="sticky top-0 z-30 mx-6 mt-6">
          <div className="flex items-center justify-between rounded-full border border-white/8 bg-[#0a0a0e]/80 px-4 py-2 backdrop-blur-xl shadow-[inset_0_1px_0_rgba(255,255,255,0.04),0_10px_40px_-20px_rgba(0,0,0,0.8)]">
            <div className="flex items-center gap-3">
              <button
                onClick={closeDetail}
                className="pill pill-hover text-xs cursor-pointer"
              >
                <ArrowLeft className="h-3.5 w-3.5" strokeWidth={1.5} />
                Back
              </button>
              <span className="hidden sm:inline text-sm font-medium text-white/70">Session Detail</span>
            </div>
            <div className="flex items-center gap-2">
              {statusBadge(s.status)}
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="glass p-5">
              <p className="text-[11px] uppercase tracking-wider text-white/40">Start Time</p>
              <p className="mt-1 text-sm font-medium">{new Date(s.start_time).toLocaleString()}</p>
            </div>
            <div className="glass p-5">
              <p className="text-[11px] uppercase tracking-wider text-white/40">Duration</p>
              <p className="mt-1 text-sm font-medium">{formatDuration(s.duration_seconds)}</p>
            </div>
            <div className="glass p-5">
              <p className="text-[11px] uppercase tracking-wider text-white/40">Events</p>
              <p className="mt-1 text-sm font-medium">{totalEvents}</p>
            </div>
          </div>

          <AnimatePresence mode="wait">
            {s.intent && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass p-5 mb-8"
              >
                <h3 className="text-sm font-semibold mb-4 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-[#7f77dd]" strokeWidth={1.5} />
                  Inferred Intent
                </h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-white/40">Type:</span>{" "}
                    <span className="font-medium text-white/80">{s.intent.session_type || "—"}</span>
                  </div>
                  <div>
                    <span className="text-white/40">Goal:</span>{" "}
                    <span className="font-medium text-white/80">{s.intent.goal || "—"}</span>
                  </div>
                  <div>
                    <span className="text-white/40">Confidence:</span>{" "}
                    <span className={`font-medium ${confidenceColor(s.intent.goal_confidence)}`}>
                      {s.intent.goal_confidence != null ? `${(s.intent.goal_confidence * 100).toFixed(0)}%` : "—"}
                    </span>
                  </div>
                  <div>
                    <span className="text-white/40">Category:</span>{" "}
                    <span className="font-medium text-white/80">{s.intent.category || "—"}</span>
                  </div>
                  {s.intent.tags.length > 0 && (
                    <div className="col-span-2 flex flex-wrap gap-1.5">
                      {s.intent.tags.map(tag => (
                        <span key={tag} className="rounded-full border border-white/10 bg-white/[0.03] px-2.5 py-0.5 text-xs text-white/60">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="glass overflow-hidden">
            <div className="px-6 py-4 flex items-center justify-between border-b border-white/5">
              <h3 className="text-sm font-semibold">Event Timeline</h3>
              <span className="text-xs text-white/40">
                {s.events.length} of {totalEvents} events
              </span>
            </div>
            <div className="divide-y divide-white/[0.03] max-h-[600px] overflow-y-auto">
              <AnimatePresence>
                {s.events.map((event, i) => {
                  const meta = eventTypeMeta(event.event_type)
                  const Icon = meta.icon
                  const time = new Date(event.timestamp).toLocaleTimeString()
                  return (
                    <motion.div
                      key={event.event_id}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.02, duration: 0.2 }}
                      className="px-6 py-3 hover:bg-white/[0.02] flex items-start gap-3 transition-colors"
                    >
                      <div className="icon-tile shrink-0 w-8 h-8">
                        <Icon className="h-3.5 w-3.5" strokeWidth={1.5} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-white/40 font-mono">{time}</p>
                        <p className="text-sm text-white/70 mt-0.5">
                          {event.event_type === "window_focus" && (event.window_title || event.process_name) && `${event.window_title || "unknown"} (${event.process_name || "?"})`}
                          {event.event_type === "screenshot" && "Screenshot captured"}
                          {event.event_type === "input_activity" && `Input: ${event.clicks_per_min ?? 0} clicks/min, ${event.keystrokes_per_min ?? 0} keys/min`}
                          {event.event_type !== "window_focus" && event.event_type !== "screenshot" && event.event_type !== "input_activity" && event.event_type}
                        </p>
                      </div>
                      <span className="text-[10px] uppercase tracking-wider text-white/30 shrink-0 mt-0.5">{meta.label}</span>
                    </motion.div>
                  )
                })}
              </AnimatePresence>
            </div>
            {hasMore && (
              <div className="px-6 py-4 border-t border-white/5 text-center">
                <button
                  onClick={loadMoreEvents}
                  disabled={detailLoading}
                  className="pill pill-hover text-xs cursor-pointer"
                >
                  <ChevronDown className="h-3.5 w-3.5" strokeWidth={1.5} />
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
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 mx-6 mt-6">
        <div className="flex items-center justify-between rounded-full border border-white/8 bg-[#0a0a0e]/80 px-4 py-2 backdrop-blur-xl shadow-[inset_0_1px_0_rgba(255,255,255,0.04),0_10px_40px_-20px_rgba(0,0,0,0.8)]">
          <div className="flex items-center gap-3">
            <div className="relative grad-border grad-border-active flex h-9 w-9 items-center justify-center">
              <div className="absolute inset-[1px] rounded-[15px] bg-[#0a0a0e]" />
              <Sparkles className="relative h-4 w-4 text-[#7f77dd]" />
            </div>
            <div className="flex flex-col leading-tight">
              <span className="text-sm font-semibold tracking-tight">Insight Monitor</span>
              <span className="text-[10px] uppercase tracking-[0.18em] text-white/40">Activity Intelligence</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`pill text-xs ${agentOnline ? "pill-hover" : ""}`}>
              <span className="relative inline-flex h-1.5 w-1.5">
                {agentOnline && (
                  <span className="absolute inset-0 animate-ping rounded-full bg-[#1d9e75] opacity-60" />
                )}
                <span className={`relative h-1.5 w-1.5 rounded-full ${agentOnline ? "bg-[#1d9e75]" : "bg-[#d85a30]"}`} />
              </span>
              <span className="text-xs">
                {loading ? "Checking..." : agentOnline ? `Online v${health?.agent?.version}` : "Offline"}
              </span>
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <p className="text-[11px] uppercase tracking-[0.22em] text-white/40">Live Monitor</p>
          <h1 className="bg-gradient-to-b from-white to-white/60 bg-clip-text text-3xl font-semibold tracking-tight text-transparent md:text-4xl">
            Sessions
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-white/55">Monitor your computer activity sessions</p>
        </div>

        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass p-8 text-center"
            >
              <div className="flex items-center justify-center gap-2 text-sm text-white/40">
                <Activity className="h-4 w-4 animate-pulse" strokeWidth={1.5} />
                Loading sessions...
              </div>
            </motion.div>
          ) : sessions.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass overflow-hidden"
            >
              <div className="px-6 py-4 border-b border-white/5">
                <p className="text-sm font-medium text-white/70">No sessions recorded yet</p>
              </div>
              <div className="p-6 text-center text-sm text-white/40">
                Start the capture agent to begin recording sessions.
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="sessions"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass overflow-hidden"
            >
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/5">
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Status</th>
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Start</th>
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Duration</th>
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Events</th>
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Apps</th>
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Type</th>
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Goal</th>
                      <th className="text-left px-4 py-3 font-medium text-white/40 text-[11px] uppercase tracking-wider">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.03]">
                    {sessions.map((s) => (
                      <motion.tr
                        key={s.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="hover:bg-white/[0.02] cursor-pointer transition-colors"
                        onClick={() => openSession(s.id)}
                      >
                        <td className="px-4 py-3">{statusBadge(s.status)}</td>
                        <td className="px-4 py-3 text-white/70">
                          {new Date(s.start_time).toLocaleString()}
                        </td>
                        <td className="px-4 py-3 text-white/70">
                          {formatDuration(s.duration_seconds)}
                        </td>
                        <td className="px-4 py-3 text-white/70">{s.event_count}</td>
                        <td className="px-4 py-3 text-white/70 max-w-[200px] truncate">
                          {(() => {
                            try {
                              const apps = JSON.parse(s.active_apps || "[]")
                              return apps.join(", ") || "—"
                            } catch {
                              return s.active_apps || "—"
                            }
                          })()}
                        </td>
                        <td className="px-4 py-3 text-white/70">{s.session_type || "—"}</td>
                        <td className="px-4 py-3 text-white/70 max-w-[200px] truncate" title={s.goal || undefined}>{s.goal || "—"}</td>
                        <td className="px-4 py-3">
                          {s.confidence != null ? (
                            <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${bgConfidence(s.confidence)}`}>
                              {(s.confidence * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <span className="text-white/30">—</span>
                          )}
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
