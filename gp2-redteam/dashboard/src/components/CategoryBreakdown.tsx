import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import type { CategorySummary } from '../types'

interface Props {
  categories: CategorySummary[]
}

const CATEGORY_LABELS: Record<string, string> = {
  hate_speech: 'Hate Speech',
  violence: 'Violence',
  misinformation: 'Misinfo',
  prompt_injection: 'Prompt Inject',
  self_harm: 'Self-Harm',
  illegal_activity: 'Illegal Activity',
  safe: 'Safe (FP check)',
}

function passColor(rate: number) {
  if (rate >= 0.8) return '#22c55e'
  if (rate >= 0.6) return '#f59e0b'
  return '#ef4444'
}

export default function CategoryBreakdown({ categories }: Props) {
  const data = categories.map(c => ({
    name: CATEGORY_LABELS[c.category] ?? c.category,
    pass_rate: Math.round(c.pass_rate * 100),
    passed: c.passed,
    failed: c.failed,
    total: c.total,
  }))

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">
        Pass Rate by Harm Category
      </h2>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 4, right: 16, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#9ca3af', fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
            labelStyle={{ color: '#f9fafb', fontWeight: 600 }}
            formatter={(value: number) => [`${value}%`, 'Pass rate']}
          />
          <Bar dataKey="pass_rate" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={passColor(entry.pass_rate / 100)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
