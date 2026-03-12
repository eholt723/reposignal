import { useState } from 'react'

const TYPE_COLORS = {
  bug: 'text-red-500 bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800',
  feature_request: 'text-blue-500 bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800',
  question: 'text-purple-500 bg-purple-50 dark:bg-purple-950 border-purple-200 dark:border-purple-800',
  docs: 'text-amber-500 bg-amber-50 dark:bg-amber-950 border-amber-200 dark:border-amber-800',
  other: 'text-gray-500 bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700',
}

const PRIORITY_COLORS = {
  high: 'text-red-500',
  medium: 'text-amber-500',
  low: 'text-green-500',
}

const TYPE_LABELS = {
  bug: 'Bug',
  feature_request: 'Feature',
  question: 'Question',
  docs: 'Docs',
  other: 'Other',
}

const ALL = 'all'

export default function IssueList({ issues }) {
  const [typeFilter, setTypeFilter] = useState(ALL)
  const [priorityFilter, setPriorityFilter] = useState(ALL)
  const [stateFilter, setStateFilter] = useState(ALL)

  if (!issues || issues.length === 0) return null

  const filtered = issues.filter(i => {
    if (typeFilter !== ALL && i.issue_type !== typeFilter) return false
    if (priorityFilter !== ALL && i.priority !== priorityFilter) return false
    if (stateFilter !== ALL && i.state !== stateFilter) return false
    return true
  })

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          Issues <span className="text-gray-400 dark:text-gray-500 font-normal">({filtered.length})</span>
        </h3>
        <div className="flex flex-wrap gap-2">
          <FilterSelect value={typeFilter} onChange={setTypeFilter} options={[
            { value: ALL, label: 'All types' },
            { value: 'bug', label: 'Bug' },
            { value: 'feature_request', label: 'Feature' },
            { value: 'question', label: 'Question' },
            { value: 'docs', label: 'Docs' },
            { value: 'other', label: 'Other' },
          ]} />
          <FilterSelect value={priorityFilter} onChange={setPriorityFilter} options={[
            { value: ALL, label: 'All priorities' },
            { value: 'high', label: 'High' },
            { value: 'medium', label: 'Medium' },
            { value: 'low', label: 'Low' },
          ]} />
          <FilterSelect value={stateFilter} onChange={setStateFilter} options={[
            { value: ALL, label: 'Open + Closed' },
            { value: 'open', label: 'Open' },
            { value: 'closed', label: 'Closed' },
          ]} />
        </div>
      </div>

      <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
        {filtered.length === 0 ? (
          <p className="text-sm text-gray-400 dark:text-gray-500 py-4 text-center">No issues match the current filters.</p>
        ) : (
          filtered.map(issue => (
            <div
              key={issue.id}
              className="flex items-start gap-3 p-3 rounded-lg border border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              {/* Type badge */}
              <span className={`mt-0.5 shrink-0 text-xs px-2 py-0.5 rounded border font-medium ${TYPE_COLORS[issue.issue_type] || TYPE_COLORS.other}`}>
                {TYPE_LABELS[issue.issue_type] || issue.issue_type || '—'}
              </span>

              {/* Title + summary */}
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-800 dark:text-gray-200 truncate">
                  #{issue.number} {issue.title}
                </p>
                {issue.summary && (
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5 truncate">{issue.summary}</p>
                )}
              </div>

              {/* Priority + state */}
              <div className="shrink-0 flex flex-col items-end gap-1">
                {issue.priority && (
                  <span className={`text-xs font-medium ${PRIORITY_COLORS[issue.priority] || 'text-gray-400'}`}>
                    {issue.priority}
                  </span>
                )}
                <span className={`text-xs ${issue.state === 'open' ? 'text-cyan-500' : 'text-gray-400 dark:text-gray-500'}`}>
                  {issue.state}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

function FilterSelect({ value, onChange, options }) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className="text-xs px-2 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-400 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-colors"
    >
      {options.map(o => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  )
}
