import { useEffect, useState } from "react"
import { ticketService, commentService } from "../api/tickets"
import { useAuth } from "../context/AuthContext"
import { showAlert } from "../components/Alert"

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
  return <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium border ${colors[priority] || "bg-slate-50 text-slate-600 border-slate-200"}`}>{PRIORITY_MAP[priority] || priority}</span>
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("es-ES", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })
}

export default function TicketDetail({ ticketId }: { ticketId: string }) {
  const { user } = useAuth()
  const [ticket, setTicket] = useState<any>(null)
  const [comments, setComments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [newComment, setNewComment] = useState("")
  const [isInternal, setIsInternal] = useState(false)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    async function fetch() {
      try {
        const [t, c] = await Promise.all([
          ticketService.getById(ticketId),
          commentService.getByTicket(ticketId),
        ])
        setTicket(t)
        setComments(c || [])
      } catch (err: any) {
        showAlert(err.message, "danger")
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [ticketId])

  async function handleStatusChange(status: string) {
    try {
      const updated = await ticketService.update(ticketId, { ...ticket, status })
      setTicket(updated)
      showAlert("Estado actualizado", "success")
    } catch (err: any) {
      showAlert(err.message, "danger")
    }
  }

  async function handleAddComment(e: React.FormEvent) {
    e.preventDefault()
    if (!newComment.trim()) return
    setSending(true)
    try {
      const comment = await commentService.create(ticketId, { body: newComment, internal: isInternal })
      setComments([...comments, comment])
      setNewComment("")
      setIsInternal(false)
    } catch (err: any) {
      showAlert(err.message, "danger")
    } finally {
      setSending(false)
    }
  }

  async function handleDeleteComment(commentId: string) {
    if (!confirm("¿Eliminar comentario?")) return
    try {
      await commentService.delete(ticketId, commentId)
      setComments(comments.filter((c) => c.id !== commentId))
      showAlert("Comentario eliminado", "success")
    } catch (err: any) {
      showAlert(err.message, "danger")
    }
  }

  if (loading) {
    return <div className="flex justify-center py-10"><div className="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full" /></div>
  }

  if (!ticket) {
    return (
      <div className="text-center py-10">
        <p className="text-slate-500 mb-4">Ticket no encontrado</p>
        <a href="#/tickets" className="text-sm text-blue-600 hover:text-blue-700 no-underline">← Volver a tickets</a>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <a href="#/tickets" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 no-underline">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Volver a tickets
      </a>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-bold text-slate-900 mb-2">{ticket.title}</h3>
            <div className="flex flex-wrap gap-2 mb-3">
              {statusBadge(ticket.status)}
              {priorityBadge(ticket.priority)}
              {ticket.category && <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-700">{ticket.category}</span>}
            </div>
            <p className="text-sm text-slate-600 whitespace-pre-wrap">{ticket.description || "Sin descripción"}</p>
          </div>
          <div className="flex gap-2 ml-4">
            {ticket.status !== "CLOSED" && (
              <select
                value={ticket.status}
                onChange={(e) => handleStatusChange(e.target.value)}
                className="px-3 py-1.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="OPEN">Abierto</option>
                <option value="IN_PROGRESS">En Proceso</option>
                <option value="CLOSED">Cerrado</option>
              </select>
            )}
          </div>
        </div>
        <div className="flex gap-6 text-xs text-slate-400 border-t border-slate-100 pt-4">
          <span><strong>Autor:</strong> {ticket.author?.name || "—"}</span>
          <span><strong>Creado:</strong> {formatDate(ticket.createdAt)}</span>
          <span><strong>Actualizado:</strong> {formatDate(ticket.updatedAt)}</span>
        </div>
        {ticket.aiSuggestion && (
          <div className="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-4 text-sm">
            <strong className="text-purple-800">Sugerencia AI:</strong>
            <p className="text-purple-700 mt-1">{ticket.aiSuggestion}</p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h4 className="font-semibold text-sm text-slate-700 mb-4">Comentarios ({comments.length})</h4>

        {comments.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-6">Sin comentarios</p>
        ) : (
          <div className="space-y-3 mb-6">
            {comments.map((c) => (
              <div key={c.id} className={`rounded-xl border p-4 ${c.internal ? "bg-amber-50 border-amber-200" : "bg-white border-slate-200"}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                      {c.author?.name?.[0]?.toUpperCase() || "U"}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-900">{c.author?.name || "Usuario"}</div>
                      <div className="text-xs text-slate-400">{formatDate(c.createdAt)}</div>
                    </div>
                  </div>
                  {(user?.role === "admin" || c.author?.id === user?.id) && (
                    <button onClick={() => handleDeleteComment(c.id)} className="text-red-400 hover:text-red-600 bg-transparent border-none cursor-pointer p-1" title="Eliminar">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  )}
                </div>
                {c.internal && <span className="inline-block text-xs bg-amber-200 text-amber-800 px-2 py-0.5 rounded mb-2 font-medium">Interno</span>}
                <p className="text-sm text-slate-700 whitespace-pre-wrap">{c.body}</p>
              </div>
            ))}
          </div>
        )}

        <form onSubmit={handleAddComment} className="space-y-3">
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            className="w-full px-4 py-3 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[80px] resize-y"
            placeholder="Escribe un comentario..."
          />
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm text-slate-600 cursor-pointer">
              <input
                type="checkbox"
                checked={isInternal}
                onChange={(e) => setIsInternal(e.target.checked)}
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              />
              Comentario interno
            </label>
            <button
              type="submit"
              disabled={sending || !newComment.trim()}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border-none cursor-pointer"
            >
              {sending ? "Enviando..." : "Enviar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
