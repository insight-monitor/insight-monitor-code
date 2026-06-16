function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-900">Insight Monitor</h1>
          <div className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full bg-green-500" title="Agent Online" />
            <span className="text-sm text-gray-500">Agent: Online</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900">Sessions</h2>
          <p className="text-gray-500 mt-1">Monitor your computer activity sessions</p>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
            <p className="text-sm font-medium text-gray-700">No sessions recorded yet</p>
          </div>
          <div className="p-6 text-center text-gray-400 text-sm">
            Start the capture agent to begin recording sessions.
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
