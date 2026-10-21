# Lote 11 — quatro módulos comuns, prova artística

Os módulos M1–M4 agora formam uma única área urbana de serviço abandonada: acesso e estacionamento, recepção, pátio de materiais, ferramentas, jardim sem manutenção e área coberta de carga. A composição preserva a função genérica dos módulos; os mapas temáticos continuam sendo alternativas, não folhas adicionais obrigatórias. O PDF da edição 0.6 permanece intacto.

- [Quatro A4 para impressão](COMUNS_4_A4.pdf), paisagem, uma face, 100%, corte de 277 × 190 mm e união sem sobreposição.
- [Mapa montado com geometria](COMUNS_COM_GEOMETRIA.png) · [arte sem interface](COMUNS_SEM_INTERFACE.png) · [comparação 0.6 → prova](COMPARACAO_B_ANTES_DEPOIS.jpg).
- [Prova de 100 mm](DETALHE_100MM_A4.pdf) · [comparação no tamanho físico](COMPARACAO_100MM_A4.pdf) · [contato das 21 conexões](provas/CONEXOES_21.jpg) · [folhas A4](provas/CONTATO_4_A4.jpg) · [escala de cinza](provas/COMUNS_CINZA.png).

A fonte funcional corresponde às zonas/conexões/portas do mapa base em `content/production/geometry_0.6.json`, com o bloqueio 7–8 removido conforme o módulo comum 0.6. São 16 zonas, 21 conexões, cinco portas e nenhum bloqueio inicial. A entrada, buscas, objetivos e surgimento continuam Z1, Z5/Z12, Z7/Z14 e Z16. Sete edições locais afastaram grade, materiais, jardim, cobertura, banco, ferramenta e portão decorativo das passagens. As 21 conexões foram inspecionadas a partir do PDF final; móveis não conferem cobertura ou bloqueio.

Nove reconstruções nativas e sete reparos formam 3817 × 2618 px para 554 × 380 mm: **175,0 ppi efetivos** no raster composto. A seção nativa de menor resolução tem 183,2 ppi no tamanho impresso e os reparos têm ao menos 530,9 ppi. A imagem global pequena serviu como guia, não como fonte ampliada para o PDF. Portas, linhas, números e símbolos são vetoriais. Medidas por seção: `fontes/resolucao.json`.

As quatro páginas A4, mapa remontado, conexões, junções, ocupação digital e escala de cinza foram renderizados. `VERIFICACOES.json` registra geometria, dimensões e fontes. **Não houve impressão física, montagem ou playtest**; pequenas transições de textura dos reparos ainda merecem avaliação em papel antes de substituir a edição distribuída.

Reconstrução pela raiz do repositório: executar `fontes/compose.py`, `fontes/build.py` e `fontes/diagnostics.py` com Python, nessa ordem.
