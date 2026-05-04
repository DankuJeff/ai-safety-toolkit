import { useEffect, useState } from 'react'
import { api } from './api'
import type { RunSummary, PromptResult, RegressionPoint } from './types'
import StatCard from './components/StatCard'
import CategoryBreakdown from './components/CategoryBreakdown'
import RegressionChart from './components/RegressionChart'
import ResultsTable from './components/ResultsTable'
import RunSelector from './components/RunSelector'

function passRateColor(rate: number): 'green' | 'yellow' | 'red' {
  if (rate >= 0.8) return 'green'
  if (rate >= 0.6) return 'yellow'
  return 'red'
}

export default function App() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string>('')
  const [summary, setSummary] = useState<RunSummary | null>(null)
  const [results, setResults] = useState<PromptResult[]>([])
  const [regression, setRegression] = useState<RegressionPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.runs(20), api.regression(10)])
      .then(([runList, regData]) => {
        setRuns(runList)
        setRegression(regData)
        if (runList.length > 0) {
          setSelectedRunId(runList[0].run_id)
        } else {
          setLoading(false)
        }
      })
      .catch(e => {
        setError(String(e))
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    if (!selectedRunId) return
    setLoading(true)
    Promise.all([api.runSummary(selectedRunId), api.runResults(selectedRunId)])
      .then(([s, r]) => {
        setSummary(s)
        setResults(r)
      })
      .catch(e => setError(String(e)))
      .finally(() => setLoading(false))
  }, [selectedRunId])

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-900/30 border border-red-800 rounded-xl p-8 max-w-md text-center">
          <p className="text-red-400 font-semibold mb-2">Connection error</p>
          <p className="text-gray-400 text-sm">{error}</p>
          <p className="text-gray-500 text-xs mt-4">Make sure the GP-2 FastAPI server is running on port 8002.</p>
        </div>
      </div>
    )
  }

  if (loading && !summary) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500 text-sm animate-pulse">Loading eval data...</p>
      </div>
    )
  }

  if (runs.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 font-semibold mb-2">No eval runs found</p>
          <p className="text-gray-500 text-sm">Run <code className="bg-gray-800 px-1 rounded">python run_eval.py</code> to generate results.</p>
        </div>
      </div>
    )
  }

  const passRatePct = summary ? `${Math.round(summary.pass_rate * 100)}%` : '—'
  const color = summary ? passRateColor(summary.pass_rate) : 'default'

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">
            LLM Safety Eval Dashboard
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">GP-2 · Red-Teaming & Safety Evaluation Framework</p>
        </div>
        {runs.length > 0 && (
          <RunSelector runs={runs} selectedRunId={selectedRunId} onSelect={setSelectedRunId} />
        )}
      </div>

      {/* Model badge */}
      {summary && (
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="bg-gray-800 border border-gray-700 rounded px-2 py-0.5 font-mono text-gray-300">
            {summary.model}
          </span>
          <span>·</span>
          <span>Run {summary.run_id.slice(0, 8)}</span>
          <span>·</span>
          <span>{new Date(summary.started_at).toLocaleString()}</span>
        </div>
      )}

      {/* Stat cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Pass Rate" value={passRatePct} color={color} sub={`${summary.passed} / ${summary.total - summary.errors} eligible`} />
          <StatCard label="Passed" value={summary.passed} color="green" />
          <StatCard label="Failed" value={summary.failed} color="red" />
          <StatCard label="Total Prompts" value={summary.total} sub={summary.errors > 0 ? `${summary.errors} errors` : undefined} />
        </div>
      )}

      {/* Category breakdown + regression side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {summary?.categories && <CategoryBreakdown categories={summary.categories} />}
        <RegressionChart data={regression} />
      </div>

      {/* Results table */}
      {results.length > 0 && <ResultsTable results={results} />}
    </div>
  )
}
