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
    return request<{ data: any[]; total: number; page: number; limit: number }>(`/tickets${qs}`)
  },
  getById: (id: string) => request<any>(`/tickets/${id}`),
  create: (data: any) => request<any>("/tickets", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: any) => request<any>(`/tickets/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (id: string) => request<any>(`/tickets/${id}`, { method: "DELETE" }),
  getStats: () => request<{ byStatus: any[]; byPriority: any[] }>("/tickets/stats"),
  classify: (data: any) => request<any>("/ai/classify", { method: "POST", body: JSON.stringify(data) }),
  suggest: (id: string) => request<any>(`/ai/tickets/${id}/suggest`),
}

export const commentService = {
  getByTicket: (ticketId: string) => request<any[]>(`/tickets/${ticketId}/comments`),
  create: (ticketId: string, data: any) =>
    request<any>(`/tickets/${ticketId}/comments`, { method: "POST", body: JSON.stringify(data) }),
  update: (ticketId: string, commentId: string, data: any) =>
    request<any>(`/tickets/${ticketId}/comments/${commentId}`, { method: "PUT", body: JSON.stringify(data) }),
  delete: (ticketId: string, commentId: string) =>
    request<any>(`/tickets/${ticketId}/comments/${commentId}`, { method: "DELETE" }),
}
