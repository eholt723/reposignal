import { useState, useEffect } from 'react'
import IssueTypeChart from './Charts/IssueTypeChart'
import PriorityChart from './Charts/PriorityChart'
import TimeSeriesChart from './Charts/TimeSeriesChart'
import OpenClosedChart from './Charts/OpenClosedChart'
import TopLabelsChart from './Charts/TopLabelsChart'
import IssueList from './IssueList'
import DraftPanel from './DraftPanel'

export default function Dashboard({ runId, repo }) {
  const [data, setData] = useState(null)
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedIssue, setSelectedIssue] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError('')
    setData(null)
    setIssues([])
    setSelectedIssue(null)

    Promise.all([
      fetch(`/api/dashboard/${runId}`).then(r => {
        if (!r.ok) throw new Error('Failed to load dashboard')
        return r.json()
      }),
      fetch(`/api/issues/${runId}`).then(r => {
        if (!r.ok) throw new Error('Failed to load issues')
        return r.json()
      }),
    ])
      .then(([dashboard, issueList]) => {
        setData(dashboard)
        setIssues(issueList)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [runId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-sm text-gray-400 dark:text-gray-500 animate-pulse">Loading dashboard…</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950 p-5">
        <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      {/* Summary stat cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard label="Total Issues" value={data.total_issues} />
        <StatCard label="Open" value={data.open_count} accent />
        <StatCard label="Closed" value={data.closed_count} />
        <StatCard label="Repo" value={repo} small />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <IssueTypeChart data={data.by_type} />
        <PriorityChart data={data.by_priority} />
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <OpenClosedChart openCount={data.open_count} closedCount={data.closed_count} />
        <TopLabelsChart data={data.top_labels} />
      </div>

      {/* Time series full width */}
      {data.issues_over_time.length > 1 && (
        <TimeSeriesChart data={data.issues_over_time} />
      )}

      {/* Issue list + draft panel */}
      <IssueList
        issues={issues}
        onSelectIssue={issue => setSelectedIssue(prev => prev?.id === issue.id ? null : issue)}
        selectedIssueId={selectedIssue?.id}
      />
      {selectedIssue && (
        <DraftPanel issue={selectedIssue} repo={repo} onClose={() => setSelectedIssue(null)} />
      )}
    </div>
  )
}

function StatCard({ label, value, accent, small }) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
      <p className="text-xs text-gray-400 dark:text-gray-500 mb-1">{label}</p>
      <p className={`font-bold truncate ${small ? 'text-sm text-gray-700 dark:text-gray-300' : 'text-2xl'} ${accent ? 'text-cyan-600 dark:text-cyan-400' : 'text-gray-900 dark:text-gray-100'}`}>
        {value}
      </p>
    </div>
  )
}
