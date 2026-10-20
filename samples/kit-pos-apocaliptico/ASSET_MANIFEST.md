# Inventário e integração

Inventário completo de arquivos e dimensões: `fontes/inventario_assets.json`; componentes e PDFs existentes: `fontes/inventario_componentes.json`. Catálogo: 24 heróis, 324 cartas, seis destinos, 198 tokens e quatro módulos. Seleção do kit: 114 cartas. Esses números não mudaram.

| Fonte nova | Pixels nativos | Origem | Integração nesta rodada |
|---|---:|---|---|
| originais/RETRATOS_01.png | 1448 × 1086 | edição integrada de seis retratos existentes | folha de arte e seis fichas |
| originais/SUPRIMENTOS.png | 1536 × 1024 | edição integrada do atlas 0.5 | conserva da prova; demais regiões não integradas |
| originais/AGUA_ISOLADA.png | 1145 × 1374 | edição integrada; objeto isolado | carta de água; corrige fragmento vizinho do atlas |
| originais/OFICINA.png | 1536 × 1024 | edição integrada do atlas 0.5 | cinco instâncias na oficina, mesmos recortes e tamanhos |
| originais/HOSPITAL.png | 1536 × 1024 | edição integrada + correção de transparência | instâncias do atlas 0.6 no hospital |
| originais/HOSPITAL_FUNDO_REJEITADO.png | 1536 × 1024 | primeira saída integrada | **rejeitada**, fundo quase opaco; não usada nos PDFs |

Os números de pixels não são DPI. `fontes/resolucao.json` registra cada recorte, dimensão física, origem e ppi; `fontes/qa_final.json` mede também as transformações reais dos PDFs. Os recortes de retratos foram medidos na imagem gerada; não houve estiramento para copiar o tamanho da imagem anterior.

## Triagem visual das fontes existentes

As quatro folhas `referencias/INVENTARIO_*.jpg` mostram 45 fontes examinadas, incluindo variantes históricas. Isso não equivale a inspeção individual ampliada de todos os arquivos derivados do repositório.

- `assets/enemies.png`: preservar os três inimigos; desgaste e silhuetas adequados. Quarto quadrante humano excluído da folha de inimigos.
- `assets/v0.5/armas.png`, `toolbox.png`, `pecas_corrigidas.png`, `viagens.png`, `assets/v0.6/bancada_topo.png`, `oficina_topo.png`: preservar nesta rodada. Já possuem materiais usados e leitura suficiente.
- `assets/portraits_01.png`: primeiros seis retratos editados; seis restantes pendentes. `portraits_02.png`: doze pendentes.
- `assets/v0.4/herois_a.png` a `herois_d.png`: 24 peões existentes preservados. Devem receber desgaste coordenado somente após revisão dos respectivos retratos; ainda não correspondem aos novos remendos.
- Hospital: atlas 0.6 revisado, demais fontes preservadas. Camas vetoriais simples e sobreposição decorativa de cadeiras/recepção são falhas herdadas, ainda pendentes.
- Condomínio (`mapa_condominio.png`, `condominio_topo.png`): plantas exuberantes e mobiliário acolhedor; prioridade seguinte de edição localizada.
- Posto (`mapa_posto.png`, `posto_topo.png`): parte da ferrugem já adequada; balcões e bombas ainda precisam de sinais de saque e manutenção interrompida.
- Estação de tratamento (`mapa_estacao.png`, `estacao_topo.png`): preservar função hídrica; acrescentar desgaste localizado de equipamento, sem redesenhar conexões.
- Mercado aprovado: integralmente preservado em `samples/mercado-b-pos-apocaliptico/`; não substituído pelos atlas mais antigos inventariados.
- Módulos comuns, abrigo, painéis, marcadores e ilustrações narrativas restantes: inventariados e preservados; revisão de direção artística ainda pendente. Nenhuma alegação de kit inteiro concluído.
