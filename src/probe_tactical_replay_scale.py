"""Executa o roteiro tático herdado contra a escala inicial de inimigos H=2..6.

O roteiro é de Lia/Ivo; falhas em H>2 identificam cobertura ausente, não defeito
comprovado do jogo. Mantém fonte e regras intocadas.
"""
import json
from math import ceil
from pathlib import Path
import review_five_days as old

ROOT=Path(__file__).resolve().parents[1]


def probe(h):
    class SizedReplay(old.Replay):
        def start(self,name):
            super().start(name)
            for _ in range(ceil(h/2)-1):self.spawn('Errante',16)
    saved=old.Replay
    old.Replay=SizedReplay
    try:
        old.run()
        return dict(heroes=h,status='PASS',note='Roteiro de dois heróis conseguiu chegar ao fim.')
    except (AssertionError, StopIteration, ValueError) as exc:
        return dict(heroes=h,status='BLOCKED',evidence=str(exc),
                    note='O roteiro de Lia/Ivo não escala automaticamente; criar ações para a equipe adicional.')
    finally:
        old.Replay=saved


if __name__=='__main__':
    rows=[probe(h) for h in range(2,7)]
    path=ROOT/'kit-final-prova/auditoria/ROTEIRO_TATICO_ESCALA.json'
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(rows)
