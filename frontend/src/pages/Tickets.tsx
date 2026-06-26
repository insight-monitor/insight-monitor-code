import { useEffect, useState, useCallback, useRef } from "react"
import { ticketService, type Ticket } from "../api/tickets"
import { showAlert } from "../components/AlertService"

const STATUS_MAP: Record<string, string> = { OPEN: "Abierto", IN_PROGRESS: "En Proceso", CLOSED: "Cerrado" }
const PRIORITY_MAP: Record<string, string> = { LOW: "Baja", MEDIUM: "Media", HIGH: "Alta", CRITICAL: "Crítica" }

function statusBadge(status: string) {
  const colors: Record<string, string> = {
    OPEN: "bg-blue-100 text-blue-700",
    IN_PROGRESS: "bg-amber-100 text-amber-700",
    CLOSED: "bg-emerald-100 text-emerald-700",
  }
  return <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status] || "bg-slate-100 text-slate-600"}`}>{STATUS_MAP[status] || status}</span>
}

function priorityBadge(priority: string) {
  const colors: Record<string, string> = {
    LOW: "bg-emerald-50 text-emerald-700 border border-emerald-200",
    MEDIUM: "bg-amber-50 text-amber-700 border border-amber-200",
    HIGH: "bg-orange-50 text-orange-700 border border-orange-200",
    CRITICAL: "bg-red-50 text-red-700 border border-red-200",
  }
  return <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[priority] || "bg-slate-50 text-slate-600 border border-slate-200"}`}>{PRIORITY_MAP[priority] || priority}</span>
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric" })
}

export default function Tickets() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const limit = 10
  const loadedRef = useRef(false)

  const loadTickets = useCallback(async () => {
    if (loadedRef.current && page === 1 && !search && !statusFilter) return
    loadedRef.current = true
    setLoading(true)
    setError("")
    try {
      const params: Record<string, string | number> = { limit, page }
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const res = await ticketService.getAll(params)
      setTickets(res.data)
      setTotal(res.total)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido")
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter, search])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadTickets()
  }, [loadTickets])

  useEffect(() => {
    const timer = setTimeout(() => {
      setPage(1)
    }, 400)
    return () => clearTimeout(timer)
  }, [search])

  const totalPages = Math.ceil(total / limit)

  async function handleDelete(id: string) {
    if (!confirm("¿Eliminar este ticket?")) return
    try {
      await ticketService.delete(id)
      showAlert("Ticket eliminado", "success")
      loadTickets()
    } catch (err) {
      showAlert(err instanceof Error ? err.message : "Error desconocido", "danger")
    }
  }

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl border border-slate-200 p-4 flex flex-wrap gap-3 items-center">
        <div className="flex items-center flex-1 min-w-[200px] max-w-[280px]">
          <span className="inline-flex items-center px-3 bg-slate-100 border border-r-0 border-slate-300 rounded-l-lg text-slate-500">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-3 py-2 border border-slate-300 rounded-r-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Buscar tickets..."
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Todos los estados</option>
          <option value="OPEN">Abierto</option>
          <option value="IN_PROGRESS">En Proceso</option>
          <option value="CLOSED">Cerrado</option>
        </select>
        <a href="#/tickets/create" className="ml-auto bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium no-underline hover:bg-blue-700 transition-colors">
          <svg className="w-4 h-4 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Nuevo Ticket
        </a>
      </div>

      {loading ? (
        <div className="flex justify-center py-10"><div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full" /></div>
      ) : error ? (
        <div className="bg-white rounded-xl border border-slate-200 p-6 text-center">
          <p className="text-red-500 text-sm">{error}</p>
        </div>
      ) : tickets.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-10 text-center text-slate-400">
          <svg className="w-12 h-12 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p>No se encontraron tickets</p>
          <a href="#/tickets/create" className="inline-block mt-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm no-underline hover:bg-blue-700">Crear primer ticket</a>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3 font-semibold">Título</th>
                <th className="text-left px-4 py-3 font-semibold">Estado</th>
                <th className="text-left px-4 py-3 font-semibold">Prioridad</th>
                <th className="text-left px-4 py-3 font-semibold">Categoría</th>
                <th className="text-left px-4 py-3 font-semibold">Autor</th>
                <th className="text-left px-4 py-3 font-semibold">Fecha</th>
                <th className="text-left px-4 py-3 font-semibold"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {tickets.map((t) => (
                <tr key={t.id} onClick={() => window.location.hash = `#/tickets/${t.id}`} className="hover:bg-slate-50 cursor-pointer">
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-900">{t.title}</div>
                    <div className="text-xs text-slate-400">{t._count?.comments || 0} comentario(s)</div>
                  </td>
                  <td className="px-4 py-3">{statusBadge(t.status)}</td>
                  <td className="px-4 py-3">{priorityBadge(t.priority)}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{t.category || "—"}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{t.author?.name || "—"}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{formatDate(t.created_at)}</td>
                  <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                    <button onClick={() => handleDelete(t.id)} className="text-red-500 hover:text-red-700 bg-transparent border-none cursor-pointer p-1" title="Eliminar">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {totalPages > 1 && (
            <div className="flex justify-center gap-1 py-4 border-t border-slate-100">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`w-8 h-8 text-sm rounded-md border-none cursor-pointer ${
                    p === page ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
