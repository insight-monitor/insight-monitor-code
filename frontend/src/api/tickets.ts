export interface Ticket {
  id: string
  title: string
  description: string
  status: string
  priority: string
  category: string
  assigned_to: string | null
  created_by: number
  created_at: string
  updated_at: string
  author?: { id: number; name: string }
  _count?: { comments: number; status?: number; priority?: number }
  aiSuggestion?: string
}

export interface TicketStats {
  byStatus: Array<{ status: string; count: number }>
  byPriority: Array<{ priority: string; count: number }>
}

export interface Comment {
  id: string
  ticket_id: string
  body: string
  internal: boolean
  created_by: number
  created_at: string
  author?: { id: number; name: string }
}

export interface ClassifyRequest {
  title: string
  description: string
}

export interface SuggestResponse {
  suggestion: string
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("token")
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (token) headers["Authorization"] = `Bearer ${token}`

  const res = await fetch(`/api${path}`, { ...options, headers })

  if (res.status === 401) {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    window.location.hash = "#/login"
    throw new Error("Sesión expirada")
  }

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.message || `Error ${res.status}`)
  }

  if (res.status === 204) return null as T
  return res.json()
}

export const ticketService = {
  getAll: (params?: Record<string, string | number>) => {
    const qs = params
      ? "?" + new URLSearchParams(
          Object.entries(params)
            .filter(([, v]) => v != null && v !== "")
            .map(([k, v]) => [k, String(v)])
        ).toString()
      : ""
    return request<{ data: Ticket[]; total: number; page: number; limit: number }>(`/tickets${qs}`)
  },
  getById: (id: string) => request<Ticket>(`/tickets/${id}`),
  create: (data: Partial<Ticket>) => request<Ticket>("/tickets", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Ticket>) => request<Ticket>(`/tickets/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/tickets/${id}`, { method: "DELETE" }),
  getStats: () => request<TicketStats>("/tickets/stats"),
  classify: (data: ClassifyRequest) => request<SuggestResponse>("/ai/classify", { method: "POST", body: JSON.stringify(data) }),
  suggest: (id: string) => request<SuggestResponse>(`/ai/tickets/${id}/suggest`),
}

export const commentService = {
  getByTicket: (ticketId: string) => request<Comment[]>(`/tickets/${ticketId}/comments`),
  create: (ticketId: string, data: Partial<Comment>) =>
    request<Comment>(`/tickets/${ticketId}/comments`, { method: "POST", body: JSON.stringify(data) }),
  update: (ticketId: string, commentId: string, data: Partial<Comment>) =>
    request<Comment>(`/tickets/${ticketId}/comments/${commentId}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (ticketId: string, commentId: string) =>
    request<void>(`/tickets/${ticketId}/comments/${commentId}`, { method: "DELETE" }),
}
