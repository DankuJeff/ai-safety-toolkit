import type { RunSummary } from '../types'

interface Props {
  runs: RunSummary[]
  selectedRunId: string
  onSelect: (runId: string) => void
}

export default function RunSelector({ runs, selectedRunId, onSelect }: Props) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-500">Run:</span>
      <select
        value={selectedRunId}
        onChange={e => onSelect(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500"
      >
        {runs.map(r => (
          <option key={r.run_id} value={r.run_id}>
            {r.run_id.slice(0, 8)} — {r.model} — {new Date(r.started_at).toLocaleString()} ({Math.round(r.pass_rate * 100)}% pass)
          </option>
        ))}
      </select>
    </div>
  )
}
