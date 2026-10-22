"""Índice de folhas selecionadas; não copia nem substitui edições anteriores."""
import json
from pathlib import Path
from final_kit_audit import ROOT, run, MAPS

OUT = ROOT / 'kit-final-prova'


def main():
    audit = run()
    base = audit['base_sheets']
    lines = ['# Índice consolidado de impressão — provas pós-apocalípticas', '',
             'Imprima a 100%, sem ajustar. Cartas 63 × 88 mm; A4 210 × 297 mm. '
             'Escolha **duplex OU recortar e colar**. Não imprima os dois métodos.', '',
             'Para jogar o capítulo inteiro, use inicial + complemento. A etapa inicial sozinha ensina o Dia 1; '
             'não substitui o manual e a campanha do complemento. Solo usa dois heróis.', '',
             '| Pessoas | Heróis | Duplex A4 | Recortar e colar A4 |',
             '|---:|---:|---:|---:|']
    for x in audit['setup_simulations']:
        lines.append(f"| {x['participants']} | {x['heroes']} | {x['duplex_sheets']} | {x['manual_sheets']} |")
    lines += ['', 'Os totais contam a folha de calibração. PDF duplex: páginas ímpares na frente, pares no verso, '
              'retrato com virada na borda longa. As folhas avulsas de mapa/painel usam uma face. '
              'A calibração manual tem duas folhas.', '',
              '## Seleção base: solo e duas pessoas (58 duplex ou 72 recortar e colar)', '',
              'Imprima uma cópia de cada arquivo abaixo. Os arquivos de cartas foram substituídos pelo lote 10 '
              '(114 IDs selecionados; mesmos textos e versos). O mapa comum foi substituído pelo lote 11.']
    for method in ('duplex', 'manual'):
        lines += ['', f'### {method.capitalize()}', '', '| Etapa | Folhas | Arquivo |', '|---|---:|---|']
        for f in audit['files']:
            if f['method'] not in ('both', method): continue
            lines.append(f"| {f['stage']} | {f['sheets']} | [{Path(f['path']).name}](../{f['path']}) |")
        lines.append(f"\nTotal: {base[method]['initial']} inicial + {base[method]['supplement']} complemento = "
                     f"**{sum(base[method].values())} folhas**.")
    lines += ['', '## Para 3–6 pessoas', '',
              'Em vez das folhas `FICHAS_LIA_IVO.pdf` (1) e `FICHAS_RESGATAVEIS.pdf` (6), '
              'imprima [FICHAS_24_HEROIS.pdf](../output/edicao-tabuleiros-v0.6/ilustrada/08_EXTRAS_OPCIONAIS/FICHAS_24_HEROIS.pdf) '
              '(12 folhas) da edição 0.6. '
              'Imprima também [HEROIS_24_RECORTAR.pdf](../output/edicao-tabuleiros-v0.6/ilustrada/04_PERSONAGENS_E_INIMIGOS/HEROIS_24_RECORTAR.pdf) '
              '(2 folhas) para os peões dos fundadores; '
              'os marcadores planos preservados trazem só Lia/Ivo e os 12 resgatáveis. '
              'Separe os peões duplicados, sem colocá-los simultaneamente no jogo. '
              'No painel, marque as barracas adicionais em T08 (H5) e T09 (H6). '
              'Na coluna Local dos registros, escreva o ID/nome do herói extra; L/I são apenas os exemplos Lia/Ivo.', '',
              'Escolha **uma** folha de seis pés de cabra e **uma** folha de reposição de Viagem/Horda. '
              'H=3–4: reposição H3_H4; H=5–6: H5_H6. A folha antiga de quatro pés de cabra '
              'é apenas alternativa se Lia e Ivo já tiverem as cartas 0001/0002; não a acumule com a universal.']
    for method in ('duplex', 'manual'):
        if method == 'duplex':
            files = ['PES_DE_CABRA_SEIS_FUNDADORES_DUPLEX.pdf', 'REPOSICAO_H3_H4_DUPLEX.pdf',
                     'REPOSICAO_H5_H6_DUPLEX.pdf']
            note = 'Escolha 1ª + (2ª **ou** 3ª): duas folhas A4 duplex.'
            paths = [f'componentes-condicionais/{x}' for x in files]
        else:
            files = [f'{stem}_{side}.pdf' for stem in ('PES_DE_CABRA_SEIS_FUNDADORES','REPOSICAO_H3_H4','REPOSICAO_H5_H6') for side in ('FRENTES','VERSOS')]
            note = ('Escolha o par Pés de cabra + um par de reposição: quatro folhas A4 de uma face. '
                    'Ao colar, espelhe as colunas do verso (esquerda↔direita), mantenha as linhas e a família; '
                    'una frente, miolo opaco e verso. IDs não aparecem no verso secreto.')
            paths = [f'componentes-condicionais/manual/{x}' for x in files]
        lines += ['', f'### Folhas condicionais {method}', '', note, '']
        lines += [f'- [{name}]({path})' for name,path in zip(files,paths)]
    lines += ['', '## Mapa de cada sessão', '',
              'Os quatro módulos comuns revisados já estão incluídos na contagem. Servem aos seis destinos. '
              'Se quiser a ambientação temática de um destino, imprima suas quatro folhas **no lugar** '
              'dos quatro comuns (+0 folha na seleção) e conserve as quatro comuns para os outros destinos. '
              'Imprimir todos os seis mapas temáticos custa 24 folhas extras; não integra os totais acima.']
    for name,path in MAPS.items():
        lines.append(f'- {name}: [{Path(path).name}](../{path}) — quatro A4 paisagem, uma face.')
    lines += ['', 'As provas e comparações dos lotes são documentos de revisão; **não são componentes adicionais**. '
              'Use uma cópia por PDF listado. Reimpressão de registro consumido é opcional e não foi somada.', '',
              '## Provas opcionais antes da partida', '',
              'Para duas pessoas, siga [o guia rápido digital](playtest/PRIMEIRA_PARTIDA_DUAS_PESSOAS.md). '
              'A seleção de 58 folhas acima permanece obrigatória; as folhas abaixo são extras.', '',
              '- [PRIMEIRA_PARTIDA_DUAS_PESSOAS.pdf](playtest/PRIMEIRA_PARTIDA_DUAS_PESSOAS.pdf): '
              '3 páginas de uma face. Lista os 18 arquivos selecionados e a ordem de preparação.',
              '- [ROTEIRO_E_REGISTRO_PLAYTEST.pdf](playtest/ROTEIRO_E_REGISTRO_PLAYTEST.pdf): '
              'imprima **somente a página 2, cinco vezes** para acompanhar o guia novo.',
              '- [OBSERVADOR_E_DEVOLUTIVA.pdf](playtest/OBSERVADOR_E_DEVOLUTIVA.pdf): '
              '2 páginas de uma face. Guia 3 + registros 5 + observador 2 = **10 folhas opcionais** '
              'para a primeira sessão de duas pessoas. A página 1 do roteiro antigo repete a preparação.',
              '- [CALIBRACAO_FRENTE_VERSO_A4.pdf](playtest/CALIBRACAO_FRENTE_VERSO_A4.pdf): '
              'uma folha duplex adicional; confira as marcas e a régua de 100 mm na própria impressora. '
              'Não substitui a calibração já incluída nas contagens. '
              'Para 3–6 pessoas, a página 3 do roteiro anterior continua disponível como orientação extra.', '',
              '## Limites desta seleção', '',
              '- A análise de preparo cobre as 2.497 combinações de vínculos para H=2–6. '
              'Há cinco trajetórias táticas fixas de cinco dias e ensaios de fases com sementes; '
              'decisões/cartas alternativas não foram reproduzidas integralmente zona por zona. '
              'Impressão física e playtest humano continuam pendentes.',
              '- Dados d6 (três), lápis, tesoura e envelopes/sleeves opacos são materiais de mesa externos.',
              '- O método manual H>2 usa frente/verso condicionais separados. Mantenha o verso secreto sem IDs visíveis.']
    (OUT/'INDICE_IMPRESSAO_CONSOLIDADO.md').write_text('\n'.join(lines)+'\n')
    print(OUT/'INDICE_IMPRESSAO_CONSOLIDADO.md')


if __name__ == '__main__': main()
