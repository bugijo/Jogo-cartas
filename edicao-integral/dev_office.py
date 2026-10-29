"""Escritório Dev do Zona Zero: papéis especializados e roteamento de tarefas.

Adaptado do Hermes Dev Office (referência apenas; nada é importado de lá). Os
papéis não ficam ativos: o Diretor aciona só os necessários, como subagentes do
Claude Code quando a tarefa justifica o custo, ou em sequência na própria
sessão. Cada papel declara entregas e critérios verificáveis; o progresso de uma
tarefa vem de `tools/progress.py`, nunca de estimativa.
"""
from __future__ import annotations

SPECIALISTS: dict[str, dict] = {
    'diretor': {
        'title': 'Diretor de Desenvolvimento',
        'scope': 'coordenação, fila, integração e publicação',
        'responsibilities': ['priorizar TASK_QUEUE.json', 'acionar só os papéis necessários',
                             'integrar entregas e publicar commits seguros'],
        'acceptance': ['check.sh full aprovado antes de publicar',
                       'checkpoint e fila atualizados', 'HEAD igual ao remoto'],
        'deliverables': ['bloco no CHECKPOINT.md', 'commits fast-forward'],
        'keywords': ['coordenar', 'integrar', 'publicar', 'commit', 'checkpoint'],
    },
    'game_designer': {
        'title': 'Game Designer Sênior',
        'scope': 'regras e experiência de jogo',
        'responsibilities': ['ler RULES/CAMPAIGN antes de mudar comportamento',
                             'registrar leituras e pedir aprovação de regra ambígua'],
        'acceptance': ['decisão registrada no MANUAL_EXPERIMENTAL.md',
                       'nenhuma regra pendente aplicada sem aprovação'],
        'deliverables': ['ruling ou pendência documentada'],
        'keywords': ['regra', 'ruling', 'manual', 'experiência'],
    },
    'board_games': {
        'title': 'Especialista em Board Games',
        'scope': 'mapas, componentes e movimentação',
        'responsibilities': ['validar mapas táticos e conexões', 'conferir custos de movimento e portas'],
        'acceptance': ['mapa carregado pelo motor sem erro', 'teste de movimento/rota'],
        'deliverables': ['dados de mapa e testes'],
        'keywords': ['mapa', 'zona', 'movimento', 'componente', 'tabuleiro'],
    },
    'card_games': {
        'title': 'Especialista em Card Games',
        'scope': 'cartas, baralhos e probabilidades',
        'responsibilities': ['auditar baralhos e distribuição', 'medir probabilidades por simulação'],
        'acceptance': ['contagem de cartas igual ao catálogo', 'probabilidade medida com sementes fixas'],
        'deliverables': ['auditoria de baralho com números'],
        'keywords': ['carta', 'baralho', 'probabilidade', 'busca', 'viagem'],
    },
    'narrativa': {
        'title': 'Designer Narrativo',
        'scope': 'história, personagens e campanhas',
        'responsibilities': ['manter coerência de contatos, pistas e arcos',
                             'marcar narrativa provisória'],
        'acceptance': ['dependências narrativas registradas', 'nenhum personagem duplicado entre arcos'],
        'deliverables': ['NARRATIVE_DEPENDENCIES.md atualizado'],
        'keywords': ['narrativa', 'pista', 'personagem', 'arco', 'história'],
    },
    'balanceamento': {
        'title': 'Especialista em Balanceamento',
        'scope': 'dificuldade e economia',
        'responsibilities': ['medir economia de comida/água/combustível',
                             'separar resultado real de protótipo'],
        'acceptance': ['sementes de ajuste 1–30; validação cega só em faixa nova',
                       'tabela real × protótipo no PLAYTEST_REPORT.md'],
        'deliverables': ['medição reprodutível'],
        'keywords': ['economia', 'dificuldade', 'balance', 'comida', 'combustível'],
    },
    'simulacao': {
        'title': 'Engenheiro de Simulação',
        'scope': 'motor, agentes e automação',
        'responsibilities': ['usar só ações públicas do motor', 'manter replays certificados intactos'],
        'acceptance': ['seed 22 verified_victory com 98 decisões', 'determinismo conferido em duas execuções'],
        'deliverables': ['código, testes e artefatos de simulação'],
        'keywords': ['motor', 'simulação', 'controlador', 'agente', 'replay', 'jogador virtual'],
    },
    'qa': {
        'title': 'QA de Jogos',
        'scope': 'bugs, regressões e regras ambíguas',
        'responsibilities': ['reproduzir defeito com teste', 'rodar check.sh full'],
        'acceptance': ['teste falha antes e passa depois', 'suíte completa aprovada'],
        'deliverables': ['teste de regressão e relatório'],
        'keywords': ['bug', 'regressão', 'teste', 'falha', 'qa'],
    },
    'grafico': {
        'title': 'Designer Gráfico',
        'scope': 'mapas, cartas, manual e impressão',
        'responsibilities': ['gerar material imprimível a partir dos dados',
                             'nunca alterar o kit físico 0.2'],
        'acceptance': ['arquivo gerado reproduzível', 'kit 0.2 sem diff'],
        'deliverables': ['PDF/PNG em output/ ou dist/'],
        'keywords': ['impressão', 'arte', 'pdf', 'layout', 'manual gráfico'],
    },
    'ux_pesquisa': {
        'title': 'Pesquisador de Experiência do Jogador',
        'scope': 'acessibilidade, clareza e público-alvo',
        'responsibilities': ['formular hipóteses a partir das simulações',
                             'planejar playtest humano'],
        'acceptance': ['hipóteses marcadas como não validadas', 'plano de playtest com métricas'],
        'deliverables': ['PLAYTEST_HUMANO.md', 'relatório por grupo'],
        'keywords': ['público', 'acessibilidade', 'clareza', 'playtest', 'persona'],
    },
}


def route(description: str) -> list[str]:
    """Papéis cujas palavras-chave aparecem na descrição; o Diretor sempre coordena."""
    text = description.lower()
    hits = [key for key, role in SPECIALISTS.items()
            if key != 'diretor' and any(word in text for word in role['keywords'])]
    return ['diretor'] + hits
