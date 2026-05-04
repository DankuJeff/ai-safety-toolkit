export interface RunSummary {
  run_id: string
  model: string
  started_at: string
  completed_at: string | null
  total: number
  passed: number
  failed: number
  errors: number
  pass_rate: number
  categories?: CategorySummary[]
}

export interface CategorySummary {
  category: string
  total: number
  passed: number
  failed: number
  errors: number
  pass_rate: number
}

export interface PromptResult {
  prompt_id: string
  category: string
  severity: number
  expected_behavior: string
  verdict: 'pass' | 'fail' | 'error'
  reason: string
  latency_ms: number
}

export interface RegressionPoint {
  run_id: string
  model: string
  date: string
  pass_rate: number
  total: number
}
