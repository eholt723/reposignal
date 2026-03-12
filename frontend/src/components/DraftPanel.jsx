import { useState, useEffect, useRef } from 'react'

export default function DraftPanel({ issue, repo, onClose }) {
  const [text, setText] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    if (!issue) return
    setText('')
    setDone(false)
    setError('')
    setStreaming(true)

    const ctrl = new AbortController()

    fetch(`/api/draft/${issue.id}`, { method: 'POST', signal: ctrl.signal })
      .then(res => {
        if (!res.ok) throw new Error('Draft request failed')
        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        function pump() {
          reader.read().then(({ value, done: readerDone }) => {
            if (readerDone) { setStreaming(false); setDone(true); return }
            buffer += decoder.decode(value, { stream: true })
            const normalized = buffer.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
            const events = normalized.split('\n\n')
            buffer = events.pop()
            for (const event of events) {
              for (const line of event.split('\n')) {
                if (!line.startsWith('data: ')) continue
                try {
                  const payload = JSON.parse(line.slice(6))
                  if (payload.chunk) setText(t => t + payload.chunk)
                  if (payload.error) { setError(payload.error); setStreaming(false) }
                  if (payload.done) { setStreaming(false); setDone(true) }
                } catch {}
              }
            }
            pump()
          }).catch(() => { setStreaming(false) })
        }
        pump()
      })
      .catch(e => {
        if (e.name !== 'AbortError') setError(e.message)
        setStreaming(false)
      })

    return () => ctrl.abort()
  }, [issue])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [text])

  if (!issue) return null

  const TYPE_LABELS = {
    bug: 'Bug', feature_request: 'Feature', question: 'Question', docs: 'Docs', other: 'Other',
  }
  const PRIORITY_COLORS = { high: 'text-red-500', medium: 'text-amber-500', low: 'text-green-500' }

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">AI Triage Draft</p>
          <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
            #{issue.number} {issue.title}
          </p>
          <div className="flex items-center gap-2 mt-1">
            {issue.issue_type && (
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {TYPE_LABELS[issue.issue_type] || issue.issue_type}
              </span>
            )}
            {issue.priority && (
              <span className={`text-xs font-medium ${PRIORITY_COLORS[issue.priority] || 'text-gray-400'}`}>
                {issue.priority} priority
              </span>
            )}
          </div>
        </div>
        {repo && issue.number && (
          <a
            href={`https://github.com/${repo}/issues/${issue.number}`}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            View Issue
          </a>
        )}
        <button
          onClick={onClose}
          className="shrink-0 p-1.5 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-gray-400 dark:text-gray-500"
          aria-label="Close"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Draft output */}
      <div className="relative min-h-[120px] rounded-lg border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-950 p-4">
        {error ? (
          <p className="text-sm text-red-500">{error}</p>
        ) : (
          <>
            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
              {text}
              {streaming && (
                <span className="inline-block w-2 h-4 ml-0.5 bg-cyan-500 animate-pulse align-text-bottom" />
              )}
            </p>
            {!text && streaming && (
              <p className="text-sm text-gray-400 dark:text-gray-500 animate-pulse">Drafting response…</p>
            )}
            {!text && !streaming && done && (
              <p className="text-sm text-gray-400 dark:text-gray-500">No response generated. Try selecting another issue.</p>
            )}
            <div ref={bottomRef} />
          </>
        )}
      </div>

      {/* Copy button */}
      {done && text && (
        <div className="flex justify-end">
          <CopyButton text={text} />
        </div>
      )}
    </div>
  )
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  function copy() {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <button
      onClick={copy}
      className="px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
    >
      {copied ? 'Copied!' : 'Copy to clipboard'}
    </button>
  )
}
