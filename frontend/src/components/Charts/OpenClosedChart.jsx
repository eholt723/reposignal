import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = { open: '#06b6d4', closed: '#6b7280' }

export default function OpenClosedChart({ openCount, closedCount }) {
  const data = [
    { name: 'Open', value: openCount, key: 'open' },
    { name: 'Closed', value: closedCount, key: 'closed' },
  ].filter(d => d.value > 0)

  const total = openCount + closedCount
  const openPct = total > 0 ? Math.round((openCount / total) * 100) : 0

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Open vs Closed</h3>
      <p className="text-xs text-gray-400 dark:text-gray-500 mb-3">{openPct}% open of {total} total</p>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={75}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry) => (
              <Cell key={entry.key} fill={COLORS[entry.key]} />
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
