import { useEffect, useState } from "react"
import { AuthProvider } from "./context/AuthContext"
import { useAuth } from "./context/useAuth"
import Layout from "./components/Layout"
import AlertContainer from "./components/Alert"
import Login from "./pages/Login"
import Register from "./pages/Register"
import TicketDashboard from "./pages/TicketDashboard"
import Tickets from "./pages/Tickets"
import TicketDetail from "./pages/TicketDetail"
import CreateTicket from "./pages/CreateTicket"
import Sessions from "./pages/Sessions"
import SessionDetail from "./pages/SessionDetail"

function Redirect({ route, isAuthenticated }: { route: string; isAuthenticated: boolean }) {
  useEffect(() => {
    window.location.hash = isAuthenticated ? "#/dashboard" : "#/login"
  }, [isAuthenticated, route])
  return null
}

const PUBLIC_ROUTES = ["/login", "/register", "/sessions"]

function _isPublicRoute(hash: string) {
  if (PUBLIC_ROUTES.includes(hash)) return true
  if (/^\/sessions\//.test(hash)) return true
  return false
}

function Router() {
  const { isAuthenticated } = useAuth()
  const [route, setRoute] = useState("")

  useEffect(() => {
    function handleRoute() {
      const hash = window.location.hash.slice(1) || "/login"
      setRoute(hash)
    }
    window.addEventListener("hashchange", handleRoute)
    handleRoute()
    return () => window.removeEventListener("hashchange", handleRoute)
  }, [])

  // Handle redirects via effect to satisfy react-hooks/immutability
  useEffect(() => {
    if (!route) return
    if (!isAuthenticated && !_isPublicRoute(route)) {
      window.location.hash = "#/login"
    }
  }, [route, isAuthenticated])

  if (!route) return null

  if (!isAuthenticated && !_isPublicRoute(route)) {
    return null
  }

  const renderPage = () => {
    const ticketDetailMatch = route.match(/^\/tickets\/([^/]+)$/)
    if (ticketDetailMatch && ticketDetailMatch[1] !== "create") {
      return <TicketDetail ticketId={ticketDetailMatch[1]} />
    }

    const sessionDetailMatch = route.match(/^\/sessions\/([^/]+)$/)
    if (sessionDetailMatch) {
      return <SessionDetail sessionId={sessionDetailMatch[1]} />
    }

    switch (route) {
      case "/login": return <Login />
      case "/register": return <Register />
      case "/dashboard": return <TicketDashboard />
      case "/tickets": return <Tickets />
      case "/tickets/create": return <CreateTicket />
      case "/sessions": return <Sessions />
      default: {
        return <Redirect route={route} isAuthenticated={isAuthenticated} />
      }
    }
  }

  if (route === "/login" || route === "/register") {
    return renderPage()
  }

  return (
    <Layout>
      {renderPage()}
    </Layout>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Router />
      <AlertContainer />
    </AuthProvider>
  )
}
