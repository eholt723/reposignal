import { useState, useEffect } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import RepoInput from './components/RepoInput'
import Dashboard from './components/Dashboard'

export default function App() {
  const [dark, setDark] = useState(() => localStorage.getItem('theme') !== 'light')
  const [runId, setRunId] = useState(null)
  const [repo, setRepo] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  async function handleAnalyze(selectedRepo) {
    setError('')
    setRunId(null)
    setRepo(selectedRepo)
    setAnalyzing(true)
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo: selectedRepo, max_issues: 100 }),
      })
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Analysis failed')
      }
      const data = await res.json()
      setRunId(data.run_id)
    } catch (e) {
      setError(e.message)
    } finally {
      setAnalyzing(false)
    }
  }

  function handleSelectHistory(histRunId, histRepo) {
    setRunId(histRunId)
    setRepo(histRepo)
    setError('')
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 transition-colors duration-200">
      <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-4 relative flex items-center justify-center">
        <div className="absolute left-6 flex items-center gap-4">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `text-sm font-medium transition-colors ${isActive ? 'text-cyan-600 dark:text-cyan-400' : 'text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'}`
            }
          >
            App
          </NavLink>
          <NavLink
            to="/about"
            className={({ isActive }) =>
              `text-sm font-medium transition-colors ${isActive ? 'text-cyan-600 dark:text-cyan-400' : 'text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'}`
            }
          >
            About
          </NavLink>
        </div>

        <div className="text-center">
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">RepoSignal</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">GitHub Issues analytics, powered by AI</p>
        </div>

        <button
          onClick={() => setDark(d => !d)}
          aria-label="Toggle dark mode"
          className="absolute right-6 p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          {dark ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-cyan-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z"/>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-cyan-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 7a5 5 0 1 0 0 10A5 5 0 0 0 12 7zm0-5a1 1 0 0 1 1 1v1a1 1 0 0 1-2 0V3a1 1 0 0 1 1-1zm0 17a1 1 0 0 1 1 1v1a1 1 0 0 1-2 0v-1a1 1 0 0 1 1-1zm9-9h1a1 1 0 0 1 0 2h-1a1 1 0 0 1 0-2zM3 12H2a1 1 0 0 1 0-2h1a1 1 0 0 1 0 2zm13.66-6.07.71-.71a1 1 0 1 1 1.41 1.41l-.71.71a1 1 0 1 1-1.41-1.41zM6.34 17.66l-.71.71a1 1 0 1 1-1.41-1.41l.71-.71a1 1 0 1 1 1.41 1.41zm11.32 0a1 1 0 0 1 0 1.41l-.71.71a1 1 0 1 1-1.41-1.41l.71-.71a1 1 0 0 1 1.41 0zM5.05 6.34a1 1 0 0 1 0 1.41l-.71.71a1 1 0 1 1-1.41-1.41l.71-.71a1 1 0 0 1 1.41 0z"/>
            </svg>
          )}
        </button>
      </header>

      <Routes>
        <Route
          path="/"
          element={
            <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
              <RepoInput
                onAnalyze={handleAnalyze}
                onSelectHistory={handleSelectHistory}
                analyzing={analyzing}
                error={error}
              />
              {runId && <Dashboard runId={runId} repo={repo} />}
            </main>
          }
        />
        <Route path="/about" element={<div className="max-w-3xl mx-auto px-4 py-12 text-gray-400 dark:text-gray-500 text-sm">About page coming in Phase 3.</div>} />
      </Routes>

      <footer className="fixed bottom-4 right-5 text-xs text-gray-400 dark:text-gray-600 text-right leading-tight">
        Created by<br />Eric Holt
      </footer>
    </div>
  )
}
