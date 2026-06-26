export interface AlertData {
  id: number
  message: string
  type: "success" | "danger" | "info"
}

let alertId = 0
export const listeners: Set<(alert: AlertData) => void> = new Set()

export function showAlert(message: string, type: "success" | "danger" | "info" = "info") {
  const alert: AlertData = { id: ++alertId, message, type }
  listeners.forEach((fn) => fn(alert))
}