export type Criterion = { id: string; label: string; weight: number; done: boolean; evidence?: string }
export type Progress = {
  project: string
  task: string
  specialist: string
  stage: string
  criteria: Criterion[]
  tests?: string
  blockers?: string[]
  approval?: string | null
  updated_at?: string
}
export type View = { progress: Progress | null; error: string | null; mtime: number }

declare module 'claude-code' {
  interface PluginState {
    'zona-zero-progresso': { view: View; isHidden: boolean }
  }
}
