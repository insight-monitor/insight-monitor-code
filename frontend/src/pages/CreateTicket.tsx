import { useState } from "react"
import { ticketService } from "../api/tickets"
import { showAlert } from "../components/Alert"

export default function CreateTicket() {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [priority, setPriority] = useState("MEDIUM")
  const [sending, setSending] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    setSending(true)
    try {
      await ticketService.create({ title: title.trim(), description: description.trim(), priority })
      showAlert("Ticket creado exitosamente", "success")
      window.location.hash = "#/tickets"
    } catch (err: any) {
      showAlert(err.message, "danger")
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <a href="#/tickets" className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 no-underline mb-4">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Volver a tickets
      </a>

      <div className="bg-white rounded-xl border border-slate-200 p-8">
        <h3 className="text-lg font-bold text-slate-900 mb-6">Nuevo Ticket</h3>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Título</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Resumen del problema"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Descripción</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[120px] resize-y"
              placeholder="Describe el problema en detalle..."
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Prioridad</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full px-4 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="LOW">Baja</option>
              <option value="MEDIUM">Media</option>
              <option value="HIGH">Alta</option>
              <option value="CRITICAL">Crítica</option>
            </select>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={sending || !title.trim()}
              className="px-6 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border-none cursor-pointer"
            >
              {sending ? "Creando..." : "Crear Ticket"}
            </button>
            <a
              href="#/tickets"
              className="px-6 py-2.5 bg-slate-100 text-slate-700 text-sm font-medium rounded-lg hover:bg-slate-200 no-underline transition-colors"
            >
              Cancelar
            </a>
          </div>
        </form>
      </div>
    </div>
  )
}
