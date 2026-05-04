import type { RunSummary, PromptResult, RegressionPoint } from './types'

const BASE = '/api/v1'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export const api = {
  latestRun: () => get<RunSummary>('/runs/latest'),
  runSummary: (runId: string) => get<RunSummary>(`/runs/${runId}/summary`),
  runResults: (runId: string) => get<PromptResult[]>(`/runs/${runId}/results`),
  runs: (limit = 20) => get<RunSummary[]>(`/runs?limit=${limit}`),
  regression: (limit = 10) => get<RegressionPoint[]>(`/regression?limit=${limit}`),
}
