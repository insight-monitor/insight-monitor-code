import { useEffect, useState } from "react"
import { ticketService } from "../api/tickets"

export default function TicketDashboard() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function fetch() {
      try {
        const [tickets, stats] = await Promise.all([
          ticketService.getAll({ limit: 5 }),
          ticketService.getStats(),
        ])
        setData({ tickets: tickets.data, stats })
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  if (loading) {
    return <div className="flex justify-center py-10"><div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full" /></div>
  }

  if (error) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500 text-sm">{error}</p>
      </div>
    )
  }

  if (!data) return null

  const counts = { OPEN: 0, IN_PROGRESS: 0, CLOSED: 0 }
  data.stats.byStatus?.forEach((s: any) => { counts[s.status as keyof typeof counts] = s._count?.status || 0 })
  const total = Object.values(counts).reduce((a, b) => a + b, 0)

  const statCards = [
    { label: "Total Tickets", value: total, icon: "M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10", color: "bg-indigo-100 text-indigo-600" },
    { label: "Abiertos", value: counts.OPEN, icon: "M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4", color: "bg-blue-100 text-blue-600" },
    { label: "En Proceso", value: counts.IN_PROGRESS, icon: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15", color: "bg-amber-100 text-amber-600" },
    { label: "Cerrados", value: counts.CLOSED, icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z", color: "bg-emerald-100 text-emerald-600" },
  ]

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        {statCards.map((card) => (
          <div key={card.label} className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-4 hover:shadow-md transition-shadow">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${card.color}`}>
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={card.icon} />
              </svg>
            </div>
            <div>
              <div className="text-xs text-slate-500 font-medium">{card.label}</div>
              <div className="text-2xl font-bold text-slate-900">{card.value}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-xl border border-slate-200">
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
              <span className="font-semibold text-sm">Tickets Recientes</span>
              <a href="#/tickets" className="text-xs text-blue-600 hover:text-blue-700 no-underline font-medium">Ver todos</a>
            </div>
            {data.tickets.length === 0 ? (
              <div className="text-center py-10 text-slate-400">
                <p>No hay tickets aún</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                      <th className="text-left px-4 py-3 font-semibold">Título</th>
                      <th className="text-left px-4 py-3 font-semibold">Estado</th>
                      <th className="text-left px-4 py-3 font-semibold">Prioridad</th>
                      <th className="text-left px-4 py-3 font-semibold">Fecha</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {data.tickets.map((t: any) => (
                      <tr key={t.id} onClick={() => window.location.hash = `#/tickets/${t.id}`} className="hover:bg-slate-50 cursor-pointer">
                        <td className="px-4 py-3">
                          <div className="font-medium text-slate-900">{t.title}</div>
                          <div className="text-xs text-slate-400">{t.author?.name || ""}</div>
                        </td>
                        <td className="px-4 py-3">{statusBadge(t.status)}</td>
                        <td className="px-4 py-3">{priorityBadge(t.priority)}</td>
                        <td className="px-4 py-3">
                          <span className="text-xs text-slate-400">{formatDate(t.createdAt)}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="bg-white rounded-xl border border-slate-200 h-full">
            <div className="px-5 py-4 border-b border-slate-100 font-semibold text-sm">Distribución por Prioridad</div>
            <div className="p-5">
              {["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((key) => {
                const cfg: Record<string, any> = {
                  LOW: { label: "Baja", color: "#10b981" },
                  MEDIUM: { label: "Media", color: "#f59e0b" },
                  HIGH: { label: "Alta", color: "#ef4444" },
                  CRITICAL: { label: "Crítica", color: "#7c3aed" },
                }
                const item = data.stats.byPriority?.find((b: any) => b.priority === key)
                const count = item?._count?.priority || 0
                const pct = total ? Math.round((count / total) * 100) : 0
                return (
                  <div key={key} className="mb-3 last:mb-0">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium">{cfg[key].label}</span>
                      <span className="text-slate-400">{count} ({pct}%)</span>
                    </div>
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: cfg[key].color }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function statusBadge(status: string) {
  const colors: Record<string, string> = {
    OPEN: "bg-blue-100 text-blue-700",
    IN_PROGRESS: "bg-amber-100 text-amber-700",
    CLOSED: "bg-emerald-100 text-emerald-700",
  }
  const labels: Record<string, string> = { OPEN: "Abierto", IN_PROGRESS: "En Proceso", CLOSED: "Cerrado" }
  return <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status] || "bg-slate-100 text-slate-600"}`}>{labels[status] || status}</span>
}

function priorityBadge(priority: string) {
  const colors: Record<string, string> = {
    LOW: "bg-emerald-50 text-emerald-700 border-emerald-200",
    MEDIUM: "bg-amber-50 text-amber-700 border-amber-200",
    HIGH: "bg-orange-50 text-orange-700 border-orange-200",
    CRITICAL: "bg-red-50 text-red-700 border-red-200",
  }
  const labels: Record<string, string> = { LOW: "Baja", MEDIUM: "Media", HIGH: "Alta", CRITICAL: "Crítica" }
  return <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors[priority] || "bg-slate-50 text-slate-600 border-slate-200"}`}>{labels[priority] || priority}</span>
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" })
}
