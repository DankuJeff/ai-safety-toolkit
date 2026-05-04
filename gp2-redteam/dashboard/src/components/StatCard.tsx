interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  color?: 'green' | 'red' | 'yellow' | 'blue' | 'default'
}

const colorMap = {
  green: 'text-green-400',
  red: 'text-red-400',
  yellow: 'text-yellow-400',
  blue: 'text-blue-400',
  default: 'text-white',
}

export default function StatCard({ label, value, sub, color = 'default' }: StatCardProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-xs text-gray-500 uppercase tracking-widest mb-1">{label}</p>
      <p className={`text-3xl font-bold ${colorMap[color]}`}>{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}
