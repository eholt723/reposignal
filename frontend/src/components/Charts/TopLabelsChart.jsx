export default function TopLabelsChart({ data }) {
  if (!data || data.length === 0) return null

  const max = data[0].count

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Top Labels</h3>
      <div className="space-y-2">
        {data.slice(0, 8).map(item => (
          <div key={item.label} className="flex items-center gap-3">
            <span className="text-xs text-gray-500 dark:text-gray-400 w-32 truncate shrink-0">{item.label}</span>
            <div className="flex-1 h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500 rounded-full"
                style={{ width: `${Math.round((item.count / max) * 100)}%` }}
              />
            </div>
            <span className="text-xs text-gray-400 dark:text-gray-500 w-6 text-right shrink-0">{item.count}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
