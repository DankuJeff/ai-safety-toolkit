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
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">
        Prompt Results
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b border-gray-800">
              <th className="pb-2 pr-4 font-medium">ID</th>
              <th className="pb-2 pr-4 font-medium">Category</th>
              <th className="pb-2 pr-4 font-medium">Sev</th>
              <th className="pb-2 pr-4 font-medium">Expected</th>
              <th className="pb-2 pr-4 font-medium">Verdict</th>
              <th className="pb-2 font-medium">Reason</th>
            </tr>
          </thead>
          <tbody>
            {results.map(r => (
              <tr key={r.prompt_id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
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
                <td className="py-2 text-gray-400 max-w-xs truncate" title={r.reason}>{r.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
