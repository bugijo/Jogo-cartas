# Jogadores programáticos — estágio inicial

`player_policies02.py` define oito políticas determinísticas: Conservador,
Explorador, Construtor, Combatente, Líder, Iniciante, Oportunista e Adversarial.
Elas escolhem destino, equipe apta e rota a partir de comida, água, dia,
ferimentos e objetivos já entregues. A escolha local básica usa somente
posições, PA, portas e inimigos revelados. Cada decisão registra uma razão
operacional e o perfil mantém memória curta de objetivos. A sonda de ação
inválida do Adversarial é separada das escolhas legais de partida.

O teste `test_player_policies02.py` cobre oito perfis nos tamanhos H2–H6:
**40 escolhas iniciais** reproduzíveis com semente 998. Outros testes verificam
exclusão de herói incapacitado e execução de uma ação local. Não há agente de
mesa independente nem simulação completa de campanha neste módulo. As
políticas ainda não administram Saque, resgate, Viagem, cerco e o segundo arco;
não usar as 40 escolhas como taxa de vitória ou evidência de equilíbrio.
