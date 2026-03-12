import { useState, useEffect } from 'react'

const PRESETS = ['fastapi/fastapi', 'microsoft/vscode', 'vercel/next.js']

export default function RepoInput({ onAnalyze, onSelectHistory, onReset, hasResult, analyzing, error }) {
  const [value, setValue] = useState('')
  const [history, setHistory] = useState([])

  useEffect(() => {
    fetch('/api/repos')
      .then(r => r.json())
      .then(setHistory)
      .catch(() => {})
  }, [])

  function submit(repo) {
    const trimmed = (repo || value).trim()
    if (!trimmed) return
    onAnalyze(trimmed)
  }

  return (
    <div className="space-y-4">
      {/* Input row */}
      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          GitHub Repository
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. fastapi/fastapi"
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && submit()}
            disabled={analyzing}
            className="flex-1 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50 transition-colors"
          />
          <button
            onClick={() => submit()}
            disabled={analyzing || !value.trim()}
            className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
          >
            Analyze
          </button>
          {hasResult && !analyzing && (
            <button
              onClick={onReset}
              className="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 text-sm font-medium transition-colors"
            >
              Reset
            </button>
          )}
        </div>

        {/* Preset buttons */}
        <div className="flex flex-wrap gap-2 mt-3">
          <span className="text-xs text-gray-400 dark:text-gray-500 self-center">Presets:</span>
          {PRESETS.map(preset => (
            <button
              key={preset}
              onClick={() => { setValue(preset); submit(preset) }}
              disabled={analyzing}
              className="px-3 py-1 rounded-md border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-xs text-gray-600 dark:text-gray-400 hover:border-cyan-500 hover:text-cyan-600 dark:hover:text-cyan-400 disabled:opacity-50 transition-colors"
            >
              {preset}
            </button>
          ))}
        </div>

        {error && (
          <p className="mt-3 text-sm text-red-500 dark:text-red-400">{error}</p>
        )}
      </div>

      {/* Repo history */}
      {history.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Previously Analyzed</h2>
          <div className="space-y-1">
            {history.map(item => (
              <button
                key={item.run_id}
                onClick={() => onSelectHistory(item.run_id, item.repo)}
                className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
                  {item.repo}
                </span>
                <div className="flex items-center gap-3 text-xs text-gray-400 dark:text-gray-500">
                  <span>{item.issue_count} issues</span>
                  <span>{new Date(item.analyzed_at).toLocaleDateString()}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
