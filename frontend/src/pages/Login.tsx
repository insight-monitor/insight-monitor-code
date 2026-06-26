import { useState, useEffect } from "react"
import { useAuth } from "../context/useAuth"

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const [email, setEmail] = useState("admin@support.com")
  const [password, setPassword] = useState("admin123")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (isAuthenticated) {
      window.location.hash = "#/dashboard"
    }
  }, [isAuthenticated])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError("")
    try {
      await login(email, password)
      window.location.hash = "#/dashboard"
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-blue-900 p-4 -m-6">
      <div className="w-full max-w-[420px] bg-white rounded-2xl p-10 shadow-2xl">
        <div className="text-center mb-8">
          <div className="text-4xl text-blue-500 mb-3 flex justify-center">
            <svg className="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Insight Monitor</h1>
          <p className="text-slate-500 text-sm mt-1">Inicia sesión en tu cuenta</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email</label>
            <div className="flex">
              <span className="inline-flex items-center px-3 bg-slate-100 border border-r-0 border-slate-300 rounded-l-lg text-slate-500">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 px-3 py-2.5 border border-slate-300 rounded-r-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="correo@ejemplo.com"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-1.5">Contraseña</label>
            <div className="flex">
              <span className="inline-flex items-center px-3 bg-slate-100 border border-r-0 border-slate-300 rounded-l-lg text-slate-500">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="flex-1 px-3 py-2.5 border border-slate-300 rounded-r-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-100 text-red-700 text-sm px-4 py-2.5 rounded-lg border border-red-200">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Ingresando...
              </span>
            ) : (
              "Iniciar Sesión"
            )}
          </button>
        </form>

        <hr className="my-6 border-slate-200" />

        <p className="text-center text-sm text-slate-500">
          ¿No tienes cuenta?{" "}
          <a href="#/register" className="text-blue-600 font-semibold no-underline hover:text-blue-700">
            Regístrate
          </a>
        </p>

        <div className="mt-4 bg-blue-50 text-blue-700 text-xs px-3 py-2 rounded-lg border border-blue-200">
          <strong>Demo:</strong> admin@support.com / admin123
        </div>
      </div>
    </div>
  )
}
