import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Progress, View } from '../types'

// Fonte única: escrita por edicao-integral/tools/progress.py a cada marco real.
const SOURCE = '/media/giovanni/HD/Projetos/Zona-Zero/docs/continuity/progress.json'
const PANE = 'zona-zero-progresso'
const POLL_MS = 3000

const view = atom({ plugin: 'zona-zero-progresso', key: 'view' } as const,
  { progress: null, error: null, mtime: 0 } as View)
const isHidden = atom({ plugin: 'zona-zero-progresso', key: 'isHidden' } as const, false)

// Percentual = soma dos pesos dos critérios concluídos (modelo do Hermes); nunca estimado.
function percent(p: Progress): number {
  const total = p.criteria.reduce((sum, c) => sum + c.weight, 0)
  const done = p.criteria.filter(c => c.done).reduce((sum, c) => sum + c.weight, 0)
  return total ? Math.round((100 * done) / total) : 0
}

function bar(value: number, width = 20): string {
  const full = Math.round((value / 100) * width)
  return '█'.repeat(full) + '░'.repeat(width - full)
}

function summary(p: Progress): string {
  const done = p.criteria.filter(c => c.done).length
  return `Zona Zero ${percent(p)}% · ${p.stage} · ${done}/${p.criteria.length}`
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'zz-progresso',
      description: 'Abre o painel de progresso do Zona Zero',
    })
    const refresh = async () => {
      try {
        const stat = await $.fs.stat(SOURCE)
        const current = await read($, view)
        if (stat.mtimeMs === current.mtime) return
        const progress = JSON.parse(await $.fs.read(SOURCE)) as Progress
        await update($, view, () => ({ progress, error: null, mtime: stat.mtimeMs }))
        $.ui.status(summary(progress))
      } catch (error) {
        await update($, view, old => ({ ...old, error: String(error) }))
      }
    }
    await refresh()
    $.clock.every(POLL_MS, refresh)

    return next(e)
  })

  on('command.run', { command: 'zz-progresso' }, async $ => {
    await update($, isHidden, () => false)
    const opened = await $.ui.open({ id: PANE, title: 'Zona Zero — progresso' })

    return { text: opened.isPlaced ? 'Painel de progresso aberto.' : 'Painel indisponível nesta superfície.' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const { progress } = await read($, view)
    if (e.props.hasSurvey || progress === null || (await read($, isHidden))) {
      return next(e)
    }
    const { Box, Button, Text } = $.ui.resolve(e)
    const value = percent(progress)
    const done = progress.criteria.filter(c => c.done).length
    const blocked = (progress.blockers ?? []).length > 0 || !!progress.approval

    return (
      <Box flexDirection="column">
        <Box>
          <Text bold>ZONA ZERO </Text>
          <Text mono color={blocked ? 'yellow' : 'green'}>[{bar(value)}] {value}%</Text>
          <Text dimColor>  {done}/{progress.criteria.length} critérios </Text>
          <Button key="hide" label="Ocultar" onPress={() => update($, isHidden, () => true)} />
        </Box>
        <Text dimColor>
          {progress.task} · {progress.specialist} · {progress.stage}
          {progress.tests ? ` · testes: ${progress.tests}` : ''}
          {progress.approval ? ` · aguarda aprovação: ${progress.approval}` : ''}
        </Text>
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text } = $.ui.resolve(e)
    const { progress, error } = await read($, view)
    if (progress === null) {
      return <Text dimColor>{error ?? 'Sem progress.json ainda.'}</Text>
    }
    const value = percent(progress)

    return (
      <Box flexDirection="column">
        <Text bold>{progress.task}</Text>
        <Text mono>[{bar(value, 24)}] {value}%</Text>
        <Text dimColor>Especialista: {progress.specialist}</Text>
        <Text dimColor>Etapa: {progress.stage}</Text>
        {progress.tests && <Text dimColor>Testes: {progress.tests}</Text>}
        {progress.criteria.map(c => (
          <Text dimColor={!c.done}>{c.done ? '✓' : '·'} {c.label} ({c.weight})</Text>
        ))}
        {(progress.blockers ?? []).map(b => <Text color="yellow">Bloqueio: {b}</Text>)}
        {progress.approval && <Text color="yellow">Aguarda aprovação: {progress.approval}</Text>}
        {progress.updated_at && <Text dimColor>Atualizado: {progress.updated_at}</Text>}
        {error && <Text color="red">{error}</Text>}
      </Box>
    )
  })
}
