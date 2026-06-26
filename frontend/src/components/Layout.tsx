import { useAuth } from "../context/AuthContext"

interface NavItem {
  path: string
  icon: string
  label: string
}

const navItems: NavItem[] = [
  { path: "/dashboard", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6", label: "Dashboard" },
  { path: "/tickets", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01", label: "Tickets" },
  { path: "/tickets/create", icon: "M12 4v16m8-8H4", label: "Nuevo Ticket" },
  { path: "/sessions", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z", label: "Monitor" },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout, isAuthenticated } = useAuth()
  const hash = window.location.hash.slice(1) || "/sessions"

  return (
    <div className="flex min-h-screen bg-slate-100">
      <nav className="w-64 bg-slate-900 flex flex-col fixed top-0 left-0 bottom-0 z-50">
        <a href="#/dashboard" className="flex items-center gap-3 px-6 py-5 border-b border-slate-800 text-white font-bold text-lg no-underline">
          <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Insight Monitor
        </a>

        <div className="flex-1 py-4 overflow-y-auto">
          <ul className="list-none m-0 p-0">
            {navItems.map(({ path, icon, label }) => {
              const isActive = hash === path
              return (
                <li key={path}>
                  <a
                    href={`#${path}`}
                    className={`flex items-center gap-3 px-6 py-3 text-sm no-underline transition-all duration-200 border-l-[3px] ${
                      isActive
                        ? "bg-slate-800 text-white border-l-blue-500"
                        : "text-slate-400 border-l-transparent hover:bg-slate-800 hover:text-white"
                    }`}
                  >
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
                    </svg>
                    {label}
                  </a>
                </li>
              )
            })}
          </ul>
        </div>

        <div className="px-6 py-4 border-t border-slate-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </div>
            <div className="min-w-0">
              <div className="text-white text-sm font-semibold truncate">{user?.name || "Usuario"}</div>
              <div className="text-slate-400 text-xs capitalize truncate">{user?.role || ""}</div>
            </div>
          </div>
          {isAuthenticated && (
            <button
              onClick={logout}
              className="w-full text-sm text-red-400 hover:text-red-300 flex items-center gap-2 bg-transparent border-none cursor-pointer px-0 py-1"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Cerrar Sesión
            </button>
          )}
        </div>
      </nav>

      <main className="flex-1 ml-64 flex flex-col min-h-screen">
        <div className="h-16 bg-white border-b border-slate-200 flex items-center px-6 sticky top-0 z-40">
          <h2 className="text-lg font-semibold text-slate-900 flex-1">
            {hash === "/dashboard" && "Dashboard"}
            {hash === "/tickets" && "Tickets"}
            {hash === "/tickets/create" && "Nuevo Ticket"}
            {hash.startsWith("/tickets/") && "Detalle del Ticket"}
            {hash === "/sessions" && "Monitor de Sesiones"}
            {hash.startsWith("/sessions/") && "Detalle de Sesión"}
            {hash === "/login" && "Iniciar Sesión"}
            {hash === "/register" && "Registro"}
          </h2>
        </div>
        <div className="flex-1 p-6">{children}</div>
      </main>
    </div>
  )
}
