import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'
import type { RegressionPoint } from '../types'

interface Props {
  data: RegressionPoint[]
}

export default function RegressionChart({ data }: Props) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">
        Pass Rate Over Time (Regression Tracking)
      </h2>
      {data.length < 2 ? (
        <p className="text-gray-500 text-sm text-center py-16">
          Run the eval suite at least twice to see regression trends.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data} margin={{ top: 4, right: 16, left: -16, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="date" tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: '#9ca3af', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
              labelStyle={{ color: '#f9fafb', fontWeight: 600 }}
              formatter={(value: number) => [`${value}%`, 'Pass rate']}
            />
            <ReferenceLine y={80} stroke="#22c55e" strokeDasharray="4 4" label={{ value: 'Target 80%', fill: '#22c55e', fontSize: 10 }} />
            <Line
              type="monotone"
              dataKey="pass_rate"
              stroke="#3b5bdb"
              strokeWidth={2}
              dot={{ fill: '#3b5bdb', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
