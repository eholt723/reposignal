import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'

const COLORS = {
  bug: '#ef4444',
  feature_request: '#3b82f6',
  question: '#a855f7',
  docs: '#f59e0b',
  other: '#6b7280',
}

const LABELS = {
  bug: 'Bug',
  feature_request: 'Feature Request',
  question: 'Question',
  docs: 'Docs',
  other: 'Other',
}

export default function IssueTypeChart({ data }) {
  const formatted = data.map(d => ({ ...d, label: LABELS[d.issue_type] || d.issue_type }))

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Issues by Type</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={formatted} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.3} />
          <XAxis dataKey="label" tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
            labelStyle={{ color: '#f3f4f6', fontSize: 12 }}
            itemStyle={{ color: '#d1d5db', fontSize: 12 }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {formatted.map((entry) => (
              <Cell key={entry.issue_type} fill={COLORS[entry.issue_type] || '#6b7280'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
