import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'

const COLORS = {
  high: '#ef4444',
  medium: '#f59e0b',
  low: '#22c55e',
}

const LABELS = { high: 'High', medium: 'Medium', low: 'Low' }

export default function PriorityChart({ data }) {
  const formatted = data.map(d => ({
    name: LABELS[d.priority] || d.priority,
    value: d.count,
    key: d.priority,
  }))

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Priority Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie
            data={formatted}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
            dataKey="value"
          >
            {formatted.map((entry) => (
              <Cell key={entry.key} fill={COLORS[entry.key] || '#6b7280'} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
            itemStyle={{ color: '#d1d5db', fontSize: 12 }}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => <span style={{ color: '#9ca3af', fontSize: 12 }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
