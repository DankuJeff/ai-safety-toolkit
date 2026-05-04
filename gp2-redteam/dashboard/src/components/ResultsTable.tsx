import { useState } from 'react'
import type { PromptResult } from '../types'

interface Props {
  results: PromptResult[]
}

const verdictStyle = {
  pass: 'bg-green-900/50 text-green-400 border border-green-800',
  fail: 'bg-red-900/50 text-red-400 border border-red-800',
  error: 'bg-gray-800 text-gray-400 border border-gray-700',
}

const behaviorStyle: Record<string, string> = {
  allow: 'text-blue-400',
  warn: 'text-yellow-400',
  refuse: 'text-red-400',
}

export default function ResultsTable({ results }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const toggle = (id: string) => setExpandedId(prev => (prev === id ? null : id))

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">
        Prompt Results
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-800">
              <th className="pb-2 pr-4 font-medium w-4"></th>
              <th className="pb-2 pr-4 font-medium">ID</th>
              <th className="pb-2 pr-4 font-medium">Category</th>
              <th className="pb-2 pr-4 font-medium">Sev</th>
              <th className="pb-2 pr-4 font-medium">Expected</th>
              <th className="pb-2 pr-4 font-medium">Verdict</th>
              <th className="pb-2 font-medium">Reason</th>
            </tr>
          </thead>
          <tbody>
            {results.map(r => {
              const isExpanded = expandedId === r.prompt_id
              return (
                <>
                  <tr
                    key={r.prompt_id}
                    onClick={() => toggle(r.prompt_id)}
                    className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors cursor-pointer select-none"
                  >
                    <td className="py-2 pr-2 text-gray-600">
                      <svg
                        className={`w-3 h-3 transition-transform duration-150 ${isExpanded ? 'rotate-90' : ''}`}
                        fill="none" stroke="currentColor" viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </td>
                    <td className="py-2 pr-4 font-mono text-gray-400">{r.prompt_id}</td>
                    <td className="py-2 pr-4 text-gray-300">{r.category.replace(/_/g, ' ')}</td>
                    <td className="py-2 pr-4 text-gray-400">{r.severity}</td>
                    <td className={`py-2 pr-4 font-medium ${behaviorStyle[r.expected_behavior] ?? 'text-gray-300'}`}>
                      {r.expected_behavior}
                    </td>
                    <td className="py-2 pr-4">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${verdictStyle[r.verdict]}`}>
                        {r.verdict}
                      </span>
                    </td>
                    <td className="py-2 text-gray-400 max-w-xs truncate">{r.reason}</td>
                  </tr>
                  {isExpanded && (
                    <tr key={`${r.prompt_id}-detail`} className="border-b border-gray-800/50 bg-gray-800/20">
                      <td />
                      <td colSpan={6} className="py-3 pr-4 pl-1">
                        <p className="text-gray-300 text-sm leading-relaxed">{r.reason}</p>
                        <p className="text-gray-600 text-xs mt-1">{r.latency_ms.toFixed(0)} ms</p>
                      </td>
                    </tr>
                  )}
                </>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
