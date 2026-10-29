#!/usr/bin/env python3
"""Progresso verificável da tarefa atual, lido pelo mod do Claude Code Desktop.

Modelo do Hermes Dev Office: o percentual é a soma dos pesos dos critérios
concluídos com evidência; nunca é estimado. Estado em
`docs/continuity/progress.json` (fora do git; o histórico fica no checkpoint).

    progress.py start "Tarefa" --specialist sim --criteria plan:Plano:10 impl:Implementação:40
    progress.py done impl --evidence "commit abc123"
    progress.py stage testes
    progress.py tests "408 OK"
    progress.py block "regra pendente" | unblock | approval "texto" | approval --clear
    progress.py show
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / 'docs' / 'continuity' / 'progress.json'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dev_office import SPECIALISTS  # noqa: E402

STAGES = ('planejamento', 'implementação', 'testes', 'simulação', 'revisão', 'concluída')


def load() -> dict:
    return json.loads(STATE.read_text(encoding='utf-8'))


def save(state: dict) -> None:
    state['updated_at'] = datetime.now().isoformat(timespec='seconds')
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, STATE)  # escrita atômica: o mod nunca lê meio arquivo


def percent(state: dict) -> int:
    total = sum(c['weight'] for c in state['criteria'])
    done = sum(c['weight'] for c in state['criteria'] if c['done'])
    return round(100 * done / total) if total else 0


def criterion(text: str) -> dict:
    key, label, weight = text.split(':', 2)
    if not key or not label or not weight.isdigit() or int(weight) < 1:
        raise argparse.ArgumentTypeError(f'critério inválido: {text} (id:rótulo:peso)')
    return {'id': key, 'label': label, 'weight': int(weight), 'done': False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest='command', required=True)
    start = sub.add_parser('start')
    start.add_argument('task')
    start.add_argument('--specialist', required=True, choices=sorted(SPECIALISTS))
    start.add_argument('--criteria', nargs='+', type=criterion, required=True)
    done = sub.add_parser('done')
    done.add_argument('id')
    done.add_argument('--evidence', required=True)
    sub.add_parser('stage').add_argument('stage', choices=STAGES)
    sub.add_parser('tests').add_argument('text')
    sub.add_parser('specialist').add_argument('key', choices=sorted(SPECIALISTS))
    sub.add_parser('block').add_argument('reason')
    sub.add_parser('unblock')
    approval = sub.add_parser('approval')
    approval.add_argument('text', nargs='?')
    approval.add_argument('--clear', action='store_true')
    sub.add_parser('show')
    args = parser.parse_args(argv)

    if args.command == 'start':
        ids = [c['id'] for c in args.criteria]
        if len(ids) != len(set(ids)):
            parser.error('ids de critério repetidos')
        state = {'project': 'Sobreviventes — Zona Zero', 'task': args.task,
                 'specialist_key': args.specialist,
                 'specialist': SPECIALISTS[args.specialist]['title'],
                 'stage': 'planejamento', 'criteria': args.criteria,
                 'tests': None, 'blockers': [], 'approval': None}
    else:
        state = load()
        if args.command == 'done':
            match = [c for c in state['criteria'] if c['id'] == args.id]
            if not match:
                parser.error(f'critério desconhecido: {args.id}')
            match[0].update(done=True, evidence=args.evidence)
        elif args.command == 'stage':
            state['stage'] = args.stage
        elif args.command == 'tests':
            state['tests'] = args.text
        elif args.command == 'specialist':
            state['specialist_key'] = args.key
            state['specialist'] = SPECIALISTS[args.key]['title']
        elif args.command == 'block':
            state['blockers'].append(args.reason)
        elif args.command == 'unblock':
            state['blockers'] = []
        elif args.command == 'approval':
            state['approval'] = None if args.clear else args.text
    if args.command != 'show':
        save(state)
    done_count = sum(c['done'] for c in state['criteria'])
    print(f"{percent(state)}% {done_count}/{len(state['criteria'])} · {state['stage']} · "
          f"{state['specialist']} · {state['task']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
