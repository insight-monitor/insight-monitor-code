import { useState, useEffect, useCallback } from "react"
import { type AlertData } from "./AlertService"
import { listeners } from "./AlertService"

export default function AlertContainer() {
  const [alerts, setAlerts] = useState<AlertData[]>([])

  const addAlert = useCallback((alert: AlertData) => {
    setAlerts((prev) => [...prev, alert])
    setTimeout(() => {
      setAlerts((prev) => prev.filter((a) => a.id !== alert.id))
    }, 4000)
  }, [])

  useEffect(() => {
    listeners.add(addAlert)
    return () => { listeners.delete(addAlert) }
  }, [addAlert])

  const colors = {
    success: "bg-green-100 text-green-800 border-green-200",
    danger: "bg-red-100 text-red-800 border-red-200",
    info: "bg-blue-100 text-blue-800 border-blue-200",
  }

  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 min-w-[280px] max-w-[360px]">
      {alerts.map((a) => (
        <div
          key={a.id}
          className={`px-4 py-3 rounded-lg border shadow-lg text-sm font-medium animate-slide-in ${colors[a.type]}`}
        >
          {a.message}
        </div>
      ))}
    </div>
  )
}
