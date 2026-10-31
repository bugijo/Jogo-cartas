# Catálogo artístico — Sobreviventes: Zona Zero

Para revisão antes da produção das artes. Gerado por `tools/art_catalog.py`: ids, nomes, quantidades e textos mecânicos vêm dos dados oficiais; descrição de arte vem de `data/art/`. Nenhuma mecânica foi alterada.

## 1. Direção artística

- **Estilo:** Pintura digital semirrealista, pós-apocalíptica, acabamento dark/grunge (textura de pincel seco, manchas, desgaste nas bordas), cenas e mapas predominantemente diurnos.
- **Ambiente:** Interior do Sudeste brasileiro meses após o colapso: Mata Atlântica degradada, pasto alto, cafezais e canaviais abandonados, rio barrento, cidade pequena com muros de chapisco, fiação caída, placas comerciais desbotadas, ônibus e motos enferrujados.
- **Pessoas:** Humanos realistas, expressivos e distintos (idade, corpo, etnia, cabelo, roupas de trabalho e remendos). Brasileiros comuns, sem estética militar de cinema.
- **Atmosfera:** Sobrevivência, abandono, perigo e reconstrução: sempre um sinal de cuidado humano (remendo, panela no fogo, horta nova) ao lado da ruína.
- **Luz:** Dia: sol de fim de manhã ou tarde nublada, sombras macias; noite só nas cartas de Cerco, Horda noturna e Passos no escuro.
- **Cartas:** Moldura escura (cinza-carvão com desgaste de metal/madeira), ilustração no terço superior/metade superior, caixa de texto clara (creme) com tipografia legível; ícone de família no canto superior esquerdo; id discreto no rodapé.
- **Tabuleiros:** Mapas táticos em vista isométrica clara (luz do dia), zonas legíveis com bordas desenhadas, portas e bloqueios marcados por ícones, sem escurecer as áreas de jogo.
- **Uso do vermelho:** Só para perigo, ferimento, Crise e destaque de regra crítica; nunca como fundo grande.
- **Proibições:** Identidade original: não copiar arte, personagens, logotipos ou composições de outros jogos ou filmes. Nada de gore explícito em close; mordida e sangue apenas sugeridos. Nomes vistos em imagens conceituais não são personagens oficiais: valem só os ids e nomes do catálogo.
- **Paleta:** verde natural `#5E7341`, verde escuro `#2F3D24`, marrom terra `#6B4A2F`, ferrugem `#9A4F25`, cinza concreto `#7B7D78`, cinza carvao `#2A2B2A`, creme leitura `#EDE6D3`, vermelho destaque `#B32A22`

## 2. Quantas ilustrações

| Item | Quantidade |
|---|---|
| Cartas no total | 400 |
| Ilustrações de carta (exclusivas) | 133 |
| Retratos de pessoas | 25 |
| Ilustrações de inimigos | 8 |
| Artes-chave de local | 9 |
| Pinturas de mapa tático | 9 |
| Tabuleiros (layout) | 3 |
| Versos (desenhos de verso) | 29 |
| **Ilustrações a pintar** | 184 |

Cartas repetidas dividem a ilustração; Saque usa a arte do Recurso com faixa do local; Projeto usa a arte da Estrutura com sobreposição de croqui; Missão e Local usam a arte-chave do local; Ajuda e Referência são diagramas.

## 3. Inconsistências documentadas (sem mudar mecânica)

1. **Heróis e especialistas são as mesmas pessoas.** Os 15 especialistas (EXP-NPC-01..14) são os heróis ZC-HER-0011..0024 do catálogo quando não jogados; só Lúcia (EXP-NPC-15) não tem ficha de herói. São 25 pessoas, um retrato cada (não 39).
2. **Dois sistemas de atributos.** O catálogo da Cisterna usa Corpo/Agilidade/Técnica; o motor regional usa Força, Agilidade, Percepção, Intelecto, Carisma e Resistência para os 10 heróis regionais. A ficha precisa decidir a apresentação (fila D-09).
3. **Material, sucata e metal.** O mesmo recurso aparece como Material (Cisterna), sucata (motor) e metal (painel). Sugestão: “Material (sucata)” na carta e “Material” no painel.
4. **Canteiro e Cerca ampliada** só existem no modelo abstrato; no acampamento em lotes não se imprimem (as 2 cartas continuam no inventário para o modelo antigo).
5. **Bancada** é peça de missão da Cisterna (ZC-PEC-0006) e obra de conhecimento (Bancada de ferramentas): nomes sugeridos diferentes para não confundir.
6. **Cartas sem id físico** (acontecimentos, profissões, obras da Comunidade, referência) recebem ids ZI-*; as chaves do motor não mudam.
7. **Imagens conceituais:** nomes vistos nelas não são personagens oficiais; valem só os ids e nomes deste catálogo.

## 4. Cartas (400) por família

### Vínculo — Cisterna 0.2 (certificada) (12 cartas, 5 ilustrações exclusivas)

**ZC-VIN-0001…ZC-VIN-0004** — Sozinho · VIN · ×4 · verso V-VIN · arte exclusiva
- Texto: Somente fundador. +0 humanos, +0 cães.
- Ilustração: Herói sentado sozinho na escada de uma casa de vila, mochila aos pés, olhando a rua vazia ao meio-dia; uma única caneca ao lado.
- Obrigatório: uma só pessoa, mochila, caneca, rua vazia

**ZC-VIN-0005…ZC-VIN-0008** — Parceiro ou parceira · VIN · ×4 · verso V-VIN · arte exclusiva
- Texto: +1 adulto civil, +1 consumidor e vaga.
- Ilustração: Duas mãos adultas apertadas sobre o capô empoeirado de um carro, alianças visíveis; ao fundo, borrado, o rosto do civil que acompanha o herói.
- Obrigatório: duas mãos adultas, aliança, civil sem arma

**ZC-VIN-0009…ZC-VIN-0010** — Filho ou filha · VIN · ×2 · verso V-VIN · arte exclusiva
- Texto: +1 criança, +1 consumidor e vaga; sem trabalho ou combate.
- Ilustração: Criança de uns 8 anos segurando a alça da mochila do adulto, tênis gasto, boné grande demais; o adulto fora de quadro, só a mão.
- Obrigatório: criança, mão adulta, sem arma

**ZC-VIN-0011** — Cachorro · VIN · ×1 · verso V-VIN · arte exclusiva
- Texto: +1 cão consumidor; sem vaga humana; alerta coletivo +1.
- Ilustração: Vira-lata caramelo de orelha em pé, coleira de corda, sentado alerta ao lado de um portão de ferro.
- Obrigatório: vira-lata caramelo, coleira de corda, postura de alerta

**ZC-VIN-0012** — Parceiro e cachorro · VIN · ×1 · verso V-VIN · arte exclusiva
- Texto: +1 adulto civil e +1 cão. Dois consumidores extras; uma vaga extra.
- Ilustração: Adulto civil agachado amarrando a coleira de um cão magro, ambos olhando para a mesma direção, estrada de terra ao fundo.
- Obrigatório: adulto civil, cão, estrada de terra

### Intenção — Cisterna 0.2 (certificada) (12 cartas, 4 ilustrações exclusivas)

**ZC-INT-0001…ZC-INT-0007** — Solidário · INT · ×7 · verso V-INT · arte exclusiva
- Texto: Permanece; após duas noites e vaga definitiva, apto no próximo amanhecer.
- Ilustração: Recém-chegado dividindo um pão em dois e oferecendo metade, sorriso cansado, luz de manhã.
- Obrigatório: pão dividido, gesto de oferta

**ZC-INT-0008…ZC-INT-0010** — Assustado · INT · ×3 · verso V-INT · arte exclusiva
- Texto: Fica, mas requer um trabalho de cuidado além de observação e vaga.
- Ilustração: Pessoa encolhida num canto com cobertor nos ombros, olhos arregalados, mãos tremendo segurando a xícara.
- Obrigatório: cobertor, xícara, olhar assustado

**ZC-INT-0011** — Oportunista · INT · ×1 · verso V-INT · arte exclusiva
- Texto: Sem Verificado nesta noite: rouba até quatro porções de conserva e grupo parte. Verificado: parte sem roubo.
- Ilustração: Mão enfiando latas de conserva numa mochila enquanto o dono olha para trás, depósito na penumbra.
- Obrigatório: latas de conserva, mochila aberta, olhar furtivo

**ZC-INT-0012** — Infiltrado · INT · ×1 · verso V-INT · arte exclusiva
- Texto: Sem Verificado nesta noite: +1 Pressão e grupo parte. Verificado: parte sem efeito.
- Ilustração: Pessoa de boné escrevendo num papel dobrado a contagem de gente e armas do abrigo, rádio pequeno no bolso.
- Obrigatório: bilhete com contagem, rádio no bolso

### Recurso — Cisterna 0.2 (certificada) (156 cartas, 10 ilustrações exclusivas)

**ZC-REC-0001…ZC-REC-0032** — Conserva → **Conservas** · REC · ×32 · verso V-REC · arte exclusiva
- Texto: 4 porções. Cursor 4 / 3 / 2 / 1. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Pilha de latas amassadas sem rótulo e com rótulo desbotado (feijão, milho, sardinha) sobre caixote, uma aberta com colher.
- Obrigatório: latas, cursor de porções 4/3/2/1

**ZC-REC-0033…ZC-REC-0068** — Água · REC · ×36 · verso V-REC · arte exclusiva
- Texto: 4 porções. Cursor 4 / 3 / 2 / 1. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Galões de 5 L e garrafas PET reaproveitadas com água límpida, gotas na superfície, sobre pano xadrez.
- Obrigatório: galão, garrafas PET, cursor de porções 4/3/2/1

**ZC-REC-0069…ZC-REC-0076** — Carne · REC · ×8 · verso V-REC · arte exclusiva
- Texto: 4 porções. Cursor 4 / 3 / 2 / 1. Carga 1. Vazio: reserva, nunca monte/estoque. Vence após refeição de hoje.
- Ilustração: Peça de carne embrulhada em folha de bananeira e barbante, sobre tábua; moscas sugeridas; faca ao lado.
- Obrigatório: folha de bananeira, carne crua, aviso visual de que estraga, cursor de porções 4/3/2/1

**ZC-REC-0077…ZC-REC-0100** — Material → **Material (sucata)** · REC · ×24 · verso V-REC · arte exclusiva
- Texto: 1 unidade. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Monte de sucata útil: chapas, parafusos em lata de tinta, arame, pedaços de cano.
- Obrigatório: sucata metálica, arame, parafusos

**ZC-REC-0101…ZC-REC-0112** — Combustível · REC · ×12 · verso V-REC · arte exclusiva
- Texto: 1 unidade. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Galão vermelho de gasolina riscado, mangueira de sifão enrolada, mancha de óleo no chão.
- Obrigatório: galão vermelho, mangueira

**ZC-REC-0113…ZC-REC-0130** — Munição · REC · ×18 · verso V-REC · arte exclusiva
- Texto: 1 unidade. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Caixa de papelão de cartuchos com poucas balas soltas e cartuchos de espingarda vermelhos.
- Obrigatório: caixa de munição, cartuchos

**ZC-REC-0131…ZC-REC-0142** — Medicamento · REC · ×12 · verso V-REC · arte exclusiva
- Texto: 1 unidade. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Blísters de comprimidos, frasco âmbar e gaze dentro de uma pochete de primeiros socorros com cruz desbotada.
- Obrigatório: blíster, frasco âmbar, gaze, cruz desbotada

**ZC-REC-0143…ZC-REC-0148** — Lona · REC · ×6 · verso V-REC · arte exclusiva
- Texto: 1 unidade. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Lona azul dobrada amarrada com corda de náilon amarela, ilhós metálicos.
- Obrigatório: lona azul, corda amarela

**ZC-REC-0149…ZC-REC-0154** — Madeira · REC · ×6 · verso V-REC · arte exclusiva
- Texto: 1 unidade. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Feixe de tábuas e caibros de demolição com pregos tortos, amarrados com arame.
- Obrigatório: tábuas, pregos tortos

**ZC-REC-0155…ZC-REC-0156** — Sementes · REC · ×2 · verso V-REC · arte exclusiva
- Texto: 1 unidade. Carga 1. Vazio: reserva, nunca monte/estoque.
- Ilustração: Saquinhos de papel kraft com sementes (feijão, milho, abóbora) escritos a lápis, numa caixa de sapato.
- Obrigatório: saquinhos de papel, letras a lápis

### Peça de missão — Cisterna 0.2 (certificada) (6 cartas, 6 ilustrações exclusivas)

**ZC-PEC-0001** — Conexões · PEC · ×1 · verso V-PEC · arte exclusiva
- Texto: Componente de projeto, não consumível de cuidado. Carga 1. Uso único ao instalar; mantenha sobre estrutura.
- Ilustração: Conexões de PVC e registro de metal sobre jornal, fita veda-rosca.
- Obrigatório: conexões de PVC, registro, veda-rosca

**ZC-PEC-0002** — Bomba · PEC · ×1 · verso V-PEC · arte exclusiva
- Texto: Componente de projeto, não consumível de cuidado. Carga 2. Uso único ao instalar; mantenha sobre estrutura.
- Ilustração: Bomba d'água periférica com carcaça azul descascada, fios soltos, sobre carrinho de mão.
- Obrigatório: bomba d'água, carrinho de mão

**ZC-PEC-0003** — Membrana · PEC · ×1 · verso V-PEC · arte exclusiva
- Texto: Componente de projeto, não consumível de cuidado. Carga 1. Uso único ao instalar; mantenha sobre estrutura.
- Ilustração: Cartucho de membrana de filtro ainda no plástico, mãos com luvas segurando como algo precioso.
- Obrigatório: cartucho de filtro, luvas

**ZC-PEC-0004** — Bateria · PEC · ×1 · verso V-PEC · arte exclusiva
- Texto: Componente de projeto, não consumível de cuidado. Carga 1. Uso único ao instalar; mantenha sobre estrutura.
- Ilustração: Bateria automotiva 60 Ah com terminais limpos e alça de corda, etiqueta de oficina.
- Obrigatório: bateria automotiva, alça de corda

**ZC-PEC-0005** — Kit de instalação médica · PEC · ×1 · verso V-PEC · arte exclusiva
- Texto: Componente de projeto, não consumível de cuidado. Carga 2. Uso único ao instalar; mantenha sobre estrutura.
- Ilustração: Maleta de alumínio aberta com suportes de soro, estetoscópio e caixas lacradas.
- Obrigatório: maleta de alumínio, suporte de soro

**ZC-PEC-0006** — Bancada → **Bancada de oficina** · PEC · ×1 · verso V-PEC · arte exclusiva
- Texto: Componente de projeto, não consumível de cuidado. Carga 2. Uso único ao instalar; mantenha sobre estrutura.
- Ilustração: Tampo de bancada com morsa presa, desmontado para transporte e amarrado com cinta.
- Obrigatório: morsa, cinta de carga

### Equipamento — Cisterna 0.2 (certificada) (18 cartas, 7 ilustrações exclusivas)

**ZC-EQU-0001…ZC-EQU-0006** — Pé de cabra · EQU · ×6 · verso V-EQU · arte exclusiva
- Texto: Próximo: Corpo vs Defesa; 1 PA, dano 1. Abre porta bloqueada por 2 PA.
- Ilustração: Pé de cabra vermelho descascado encostado numa porta de aço arrombada.
- Obrigatório: pé de cabra, porta arrombada

**ZC-EQU-0007…ZC-EQU-0008** — Faca · EQU · ×2 · verso V-EQU · arte exclusiva
- Texto: Próximo, dano 1, 1 PA. +1 Corpo no primeiro ataque da rodada.
- Ilustração: Faca de cozinha com cabo enrolado em fita isolante, bainha de garrafa PET cortada.
- Obrigatório: faca, fita isolante

**ZC-EQU-0009…ZC-EQU-0010** — Machado · EQU · ×2 · verso V-EQU · arte exclusiva
- Texto: Próximo, dano 2; 2 PA por ataque.
- Ilustração: Machado de lenha com cabo gasto cravado num toco.
- Obrigatório: machado, toco

**ZC-EQU-0011…ZC-EQU-0012** — Pistola · EQU · ×2 · verso V-EQU · arte exclusiva
- Texto: Mesma/adjacente visível; Agilidade vs Defesa. 1 PA+1 Munição, dano 1; gera Ruído.
- Ilustração: Pistola sobre pano de prato, carregador ao lado, com sinal de ruído sugerido (ondas sonoras gráficas discretas).
- Obrigatório: pistola, carregador, ícone de Ruído

**ZC-EQU-0013** — Espingarda · EQU · ×1 · verso V-EQU · arte exclusiva
- Texto: Mesma/adjacente visível; Agilidade. 1 PA+1 Munição, dano 2, uma vez/rodada; Ruído.
- Ilustração: Espingarda calibre 12 de cano curto pendurada num prego, cartuchos no cinto ao lado.
- Obrigatório: espingarda, cartucheira, ícone de Ruído

**ZC-EQU-0014…ZC-EQU-0016** — Ferramentas · EQU · ×3 · verso V-EQU · arte exclusiva
- Texto: Permite abrir bloqueio por 2 PA e reparar van. Carga 1; não é consumido salvo projeto que o exige.
- Ilustração: Caixa de ferramentas aberta: chave de fenda, alicate, chave inglesa, fita.
- Obrigatório: caixa de ferramentas, chave inglesa

**ZC-EQU-0017…ZC-EQU-0018** — Lanterna · EQU · ×2 · verso V-EQU · arte exclusiva
- Texto: Uma vez/visita, permite olhar carta Saque do topo e devolver; 1 PA. Carga 1.
- Ilustração: Lanterna de mão acesa iluminando uma prateleira de saque no escuro; único cartão de Equipamento com interior escuro.
- Obrigatório: facho de luz, prateleira

### Saque — Cisterna 0.2 (certificada) (36 cartas, 0 ilustrações exclusivas)

**ZC-SAQ-0001** — Mercado: Conserva · SAQ · ×1 · verso V-SAQ (Mercado) · arte compartilhada:REC:Conserva
- Texto: Ganhe 1 carta(s) física(s) Conserva da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Conserva com faixa do local Mercado sobre o mapa.
- Obrigatório: faixa Mercado, arte REC:Conserva

**ZC-SAQ-0002** — Mercado: Água · SAQ · ×1 · verso V-SAQ (Mercado) · arte compartilhada:REC:Água
- Texto: Ganhe 1 carta(s) física(s) Água da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Água com faixa do local Mercado sobre o mapa.
- Obrigatório: faixa Mercado, arte REC:Água

**ZC-SAQ-0003** — Mercado: Material · SAQ · ×1 · verso V-SAQ (Mercado) · arte compartilhada:REC:Material
- Texto: Ganhe 1 carta(s) física(s) Material da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Material com faixa do local Mercado sobre o mapa.
- Obrigatório: faixa Mercado, arte REC:Material

**ZC-SAQ-0004** — Mercado: Munição · SAQ · ×1 · verso V-SAQ (Mercado) · arte compartilhada:REC:Munição
- Texto: Ganhe 2 carta(s) física(s) Munição da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Munição com faixa do local Mercado sobre o mapa.
- Obrigatório: faixa Mercado, arte REC:Munição

**ZC-SAQ-0005** — Mercado: Medicamento · SAQ · ×1 · verso V-SAQ (Mercado) · arte compartilhada:REC:Medicamento
- Texto: Ganhe 1 carta(s) física(s) Medicamento da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Medicamento com faixa do local Mercado sobre o mapa.
- Obrigatório: faixa Mercado, arte REC:Medicamento

**ZC-SAQ-0006** — Mercado: Carne · SAQ · ×1 · verso V-SAQ (Mercado) · arte compartilhada:REC:Carne
- Texto: Ganhe 1 carta(s) física(s) Carne da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Carne com faixa do local Mercado sobre o mapa.
- Obrigatório: faixa Mercado, arte REC:Carne

**ZC-SAQ-0007** — Hospital: Conserva · SAQ · ×1 · verso V-SAQ (Hospital) · arte compartilhada:REC:Conserva
- Texto: Ganhe 1 carta(s) física(s) Conserva da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Conserva com faixa do local Hospital sobre o mapa.
- Obrigatório: faixa Hospital, arte REC:Conserva

**ZC-SAQ-0008** — Hospital: Água · SAQ · ×1 · verso V-SAQ (Hospital) · arte compartilhada:REC:Água
- Texto: Ganhe 1 carta(s) física(s) Água da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Água com faixa do local Hospital sobre o mapa.
- Obrigatório: faixa Hospital, arte REC:Água

**ZC-SAQ-0009** — Hospital: Material · SAQ · ×1 · verso V-SAQ (Hospital) · arte compartilhada:REC:Material
- Texto: Ganhe 1 carta(s) física(s) Material da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Material com faixa do local Hospital sobre o mapa.
- Obrigatório: faixa Hospital, arte REC:Material

**ZC-SAQ-0010** — Hospital: Munição · SAQ · ×1 · verso V-SAQ (Hospital) · arte compartilhada:REC:Munição
- Texto: Ganhe 2 carta(s) física(s) Munição da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Munição com faixa do local Hospital sobre o mapa.
- Obrigatório: faixa Hospital, arte REC:Munição

**ZC-SAQ-0011** — Hospital: Medicamento · SAQ · ×1 · verso V-SAQ (Hospital) · arte compartilhada:REC:Medicamento
- Texto: Ganhe 1 carta(s) física(s) Medicamento da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Medicamento com faixa do local Hospital sobre o mapa.
- Obrigatório: faixa Hospital, arte REC:Medicamento

**ZC-SAQ-0012** — Hospital: Carne · SAQ · ×1 · verso V-SAQ (Hospital) · arte compartilhada:REC:Carne
- Texto: Ganhe 1 carta(s) física(s) Carne da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Carne com faixa do local Hospital sobre o mapa.
- Obrigatório: faixa Hospital, arte REC:Carne

**ZC-SAQ-0013** — Oficina: Conserva · SAQ · ×1 · verso V-SAQ (Oficina) · arte compartilhada:REC:Conserva
- Texto: Ganhe 1 carta(s) física(s) Conserva da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Conserva com faixa do local Oficina sobre o mapa.
- Obrigatório: faixa Oficina, arte REC:Conserva

**ZC-SAQ-0014** — Oficina: Água · SAQ · ×1 · verso V-SAQ (Oficina) · arte compartilhada:REC:Água
- Texto: Ganhe 1 carta(s) física(s) Água da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Água com faixa do local Oficina sobre o mapa.
- Obrigatório: faixa Oficina, arte REC:Água

**ZC-SAQ-0015** — Oficina: Material · SAQ · ×1 · verso V-SAQ (Oficina) · arte compartilhada:REC:Material
- Texto: Ganhe 1 carta(s) física(s) Material da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Material com faixa do local Oficina sobre o mapa.
- Obrigatório: faixa Oficina, arte REC:Material

**ZC-SAQ-0016** — Oficina: Munição · SAQ · ×1 · verso V-SAQ (Oficina) · arte compartilhada:REC:Munição
- Texto: Ganhe 2 carta(s) física(s) Munição da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Munição com faixa do local Oficina sobre o mapa.
- Obrigatório: faixa Oficina, arte REC:Munição

**ZC-SAQ-0017** — Oficina: Medicamento · SAQ · ×1 · verso V-SAQ (Oficina) · arte compartilhada:REC:Medicamento
- Texto: Ganhe 1 carta(s) física(s) Medicamento da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Medicamento com faixa do local Oficina sobre o mapa.
- Obrigatório: faixa Oficina, arte REC:Medicamento

**ZC-SAQ-0018** — Oficina: Carne · SAQ · ×1 · verso V-SAQ (Oficina) · arte compartilhada:REC:Carne
- Texto: Ganhe 1 carta(s) física(s) Carne da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Carne com faixa do local Oficina sobre o mapa.
- Obrigatório: faixa Oficina, arte REC:Carne

**ZC-SAQ-0019** — Posto: Conserva · SAQ · ×1 · verso V-SAQ (Posto) · arte compartilhada:REC:Conserva
- Texto: Ganhe 1 carta(s) física(s) Conserva da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Conserva com faixa do local Posto sobre o mapa.
- Obrigatório: faixa Posto, arte REC:Conserva

**ZC-SAQ-0020** — Posto: Água · SAQ · ×1 · verso V-SAQ (Posto) · arte compartilhada:REC:Água
- Texto: Ganhe 1 carta(s) física(s) Água da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Água com faixa do local Posto sobre o mapa.
- Obrigatório: faixa Posto, arte REC:Água

**ZC-SAQ-0021** — Posto: Material · SAQ · ×1 · verso V-SAQ (Posto) · arte compartilhada:REC:Material
- Texto: Ganhe 1 carta(s) física(s) Material da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Material com faixa do local Posto sobre o mapa.
- Obrigatório: faixa Posto, arte REC:Material

**ZC-SAQ-0022** — Posto: Munição · SAQ · ×1 · verso V-SAQ (Posto) · arte compartilhada:REC:Munição
- Texto: Ganhe 2 carta(s) física(s) Munição da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Munição com faixa do local Posto sobre o mapa.
- Obrigatório: faixa Posto, arte REC:Munição

**ZC-SAQ-0023** — Posto: Medicamento · SAQ · ×1 · verso V-SAQ (Posto) · arte compartilhada:REC:Medicamento
- Texto: Ganhe 1 carta(s) física(s) Medicamento da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Medicamento com faixa do local Posto sobre o mapa.
- Obrigatório: faixa Posto, arte REC:Medicamento

**ZC-SAQ-0024** — Posto: Carne · SAQ · ×1 · verso V-SAQ (Posto) · arte compartilhada:REC:Carne
- Texto: Ganhe 1 carta(s) física(s) Carne da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Carne com faixa do local Posto sobre o mapa.
- Obrigatório: faixa Posto, arte REC:Carne

**ZC-SAQ-0025** — Condomínio: Conserva · SAQ · ×1 · verso V-SAQ (Condomínio) · arte compartilhada:REC:Conserva
- Texto: Ganhe 1 carta(s) física(s) Conserva da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Conserva com faixa do local Condomínio sobre o mapa.
- Obrigatório: faixa Condomínio, arte REC:Conserva

**ZC-SAQ-0026** — Condomínio: Água · SAQ · ×1 · verso V-SAQ (Condomínio) · arte compartilhada:REC:Água
- Texto: Ganhe 1 carta(s) física(s) Água da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Água com faixa do local Condomínio sobre o mapa.
- Obrigatório: faixa Condomínio, arte REC:Água

**ZC-SAQ-0027** — Condomínio: Material · SAQ · ×1 · verso V-SAQ (Condomínio) · arte compartilhada:REC:Material
- Texto: Ganhe 1 carta(s) física(s) Material da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Material com faixa do local Condomínio sobre o mapa.
- Obrigatório: faixa Condomínio, arte REC:Material

**ZC-SAQ-0028** — Condomínio: Munição · SAQ · ×1 · verso V-SAQ (Condomínio) · arte compartilhada:REC:Munição
- Texto: Ganhe 2 carta(s) física(s) Munição da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Munição com faixa do local Condomínio sobre o mapa.
- Obrigatório: faixa Condomínio, arte REC:Munição

**ZC-SAQ-0029** — Condomínio: Medicamento · SAQ · ×1 · verso V-SAQ (Condomínio) · arte compartilhada:REC:Medicamento
- Texto: Ganhe 1 carta(s) física(s) Medicamento da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Medicamento com faixa do local Condomínio sobre o mapa.
- Obrigatório: faixa Condomínio, arte REC:Medicamento

**ZC-SAQ-0030** — Condomínio: Carne · SAQ · ×1 · verso V-SAQ (Condomínio) · arte compartilhada:REC:Carne
- Texto: Ganhe 1 carta(s) física(s) Carne da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Carne com faixa do local Condomínio sobre o mapa.
- Obrigatório: faixa Condomínio, arte REC:Carne

**ZC-SAQ-0031** — Estação: Conserva · SAQ · ×1 · verso V-SAQ (Estação) · arte compartilhada:REC:Conserva
- Texto: Ganhe 1 carta(s) física(s) Conserva da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Conserva com faixa do local Estação sobre o mapa.
- Obrigatório: faixa Estação, arte REC:Conserva

**ZC-SAQ-0032** — Estação: Água · SAQ · ×1 · verso V-SAQ (Estação) · arte compartilhada:REC:Água
- Texto: Ganhe 1 carta(s) física(s) Água da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Água com faixa do local Estação sobre o mapa.
- Obrigatório: faixa Estação, arte REC:Água

**ZC-SAQ-0033** — Estação: Material · SAQ · ×1 · verso V-SAQ (Estação) · arte compartilhada:REC:Material
- Texto: Ganhe 1 carta(s) física(s) Material da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Material com faixa do local Estação sobre o mapa.
- Obrigatório: faixa Estação, arte REC:Material

**ZC-SAQ-0034** — Estação: Munição · SAQ · ×1 · verso V-SAQ (Estação) · arte compartilhada:REC:Munição
- Texto: Ganhe 2 carta(s) física(s) Munição da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Munição com faixa do local Estação sobre o mapa.
- Obrigatório: faixa Estação, arte REC:Munição

**ZC-SAQ-0035** — Estação: Medicamento · SAQ · ×1 · verso V-SAQ (Estação) · arte compartilhada:REC:Medicamento
- Texto: Ganhe 1 carta(s) física(s) Medicamento da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Medicamento com faixa do local Estação sobre o mapa.
- Obrigatório: faixa Estação, arte REC:Medicamento

**ZC-SAQ-0036** — Estação: Carne · SAQ · ×1 · verso V-SAQ (Estação) · arte compartilhada:REC:Carne
- Texto: Ganhe 1 carta(s) física(s) Carne da reserva; carga 1/carta. Retire um uso de busca e descarte aqui. Não repõe em nova visita.
- Ilustração: Arte do recurso Carne com faixa do local Estação sobre o mapa.
- Obrigatório: faixa Estação, arte REC:Carne

### Viagem — Cisterna 0.2 (certificada) (12 cartas, 12 ilustrações exclusivas)

**ZC-VIA-0001** — Rua vazia · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Sem efeito adicional.
- Ilustração: Rua de cidade pequena ao meio-dia, carros parados, varal com roupa, nenhum movimento.
- Obrigatório: rua vazia, carros parados

**ZC-VIA-0002** — Chuva ácida de fuligem → **Chuva de fuligem** · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Escolham perder uma porção água levada OU cada herói ganha 1 fadiga.
- Ilustração: Chuva cinza manchando o para-brisa de uma van, heróis cobrindo galões com o corpo.
- Obrigatório: chuva escura, galões protegidos

**ZC-VIA-0003** — Sinal de passagem · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Se voltarem hoje por esta rota, ignorem a próxima Viagem normal da volta, mas paguem tempo e combustível.
- Ilustração: Seta pintada com spray num muro e pedras empilhadas indicando atalho.
- Obrigatório: seta de spray, pedras empilhadas

**ZC-VIA-0004** — Barricada · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Paguem 1 Material levado OU +1 Pressão externa. Sem tempo extra.
- Ilustração: Barricada de carros e móveis numa ponte de concreto, passagem estreita.
- Obrigatório: carros, móveis, passagem estreita

**ZC-VIA-0005** — Emboscada · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Use M1: Z1/2/5/6. Grupo Z1; ceil(H/2) Errantes e surgimento em Z6. Porta 1–5 fechada comum; pressão local 0. Uma rodada completa obrigatória, mesmo relógio. Saída Z1 livre. Sem Saque; retome a viagem sem pagar de novo o trecho.
- Ilustração: Errantes saindo do canavial dos dois lados da estrada de terra, heróis recuando de costas.
- Obrigatório: canavial, errantes, heróis cercados

**ZC-VIA-0006** — Vizinho na janela · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Podem entregar 1 comida+1 água levadas: +1 Moral, máximo 5. Sem resgate.
- Ilustração: Idosa acenando atrás de grade de janela com cortina de renda, pedindo água.
- Obrigatório: janela com grade, idosa, gesto de pedido

**ZC-VIA-0007** — Ruído distante · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: +1 Pressão externa.
- Ilustração: Fumaça e pássaros levantando voo ao longe, sobre o morro.
- Obrigatório: fumaça distante, revoada

**ZC-VIA-0008** — Desvio sinalizado · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Sem efeito; registrem rota conhecida.
- Ilustração: Placa de obra 'DESVIO' tombada e uma trilha alternativa pela fazenda.
- Obrigatório: placa DESVIO, trilha

**ZC-VIA-0009** — Cão perdido · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Sem vínculo humano: se uma família sem cão aceitar, +1 cão à chegada. Consome uma comida e uma água na refeição; não há custo adicional na estrada. Caso contrário segue seguro no local, sem punição.
- Ilustração: Cão sujo seguindo o grupo a distância pela estrada, rabo baixo.
- Obrigatório: cão, distância

**ZC-VIA-0010** — Ferragens · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Ida: deixe 1 Material no chão Z1 do destino; coletar custa 1 PA. Volta: acrescente 1 Material ao estoque ao chegar. Uma unidade por ocorrência, nunca ambos.
- Ilustração: Ferro-velho à beira da estrada com peças úteis expostas ao sol.
- Obrigatório: ferro-velho, sucata útil

**ZC-VIA-0011** — Ponte avistada · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Marque Ponte conhecida; não encaminha de graça.
- Ilustração: Vista do alto de uma ponte de ferro sobre rio barrento com bandeira improvisada.
- Obrigatório: ponte de ferro, bandeira

**ZC-VIA-0012** — Caminho limpo · VIA · ×1 · verso V-VIA · arte exclusiva
- Texto: Sem efeito. Não gera recursos.
- Ilustração: Estrada de chão reta entre eucaliptos, céu aberto.
- Obrigatório: estrada reta, eucaliptos

### Horda — Cisterna 0.2 (certificada) (9 cartas, 4 ilustrações exclusivas)

**ZC-HOR-0001…ZC-HOR-0004** — Arrastar · HOR · ×4 · verso V-HOR · arte exclusiva
- Texto: Coloque 1 Errante em S.
- Ilustração: Errante solitário arrastando o pé pelo corredor de um mercado, carrinho tombado.
- Obrigatório: 1 errante, pé arrastado

**ZC-HOR-0005…ZC-HOR-0006** — Corrida · HOR · ×2 · verso V-HOR · arte exclusiva
- Texto: Coloque 1 Corredor em S.
- Ilustração: Corredor em disparada, borrão de movimento, boca aberta, vindo pelo estacionamento.
- Obrigatório: 1 corredor, movimento rápido

**ZC-HOR-0007…ZC-HOR-0008** — Aglomerado · HOR · ×2 · verso V-HOR · arte exclusiva
- Texto: Coloque ceil(H/2) Errantes em S.
- Ilustração: Grupo de errantes pressionando uma porta de vidro, mãos espalmadas.
- Obrigatório: vários errantes, porta de vidro

**ZC-HOR-0009** — Peso morto · HOR · ×1 · verso V-HOR · arte exclusiva
- Texto: Coloque 1 Bruto em S.
- Ilustração: Bruto enorme de macacão de frigorífico atravessando uma parede de drywall.
- Obrigatório: 1 bruto, parede quebrada

### Cerco — Cisterna 0.2 (certificada) (6 cartas, 6 ilustrações exclusivas)

**ZC-CER-0001** — Portão pressionado · CER · ×1 · verso V-CER · arte exclusiva
- Texto: Força 4. Zumbis. Defesa: portão 2 + torre 1 + cão 1 + até 3 vigias 4+ + até 2 Munições. Consulte perdas no painel.
- Ilustração: Noite: portão do abrigo envergando sob mãos e corpos, lanternas dos vigias no alto.
- Obrigatório: portão, vigias com lanterna, noite

**ZC-CER-0002** — Fila na cerca · CER · ×1 · verso V-CER · arte exclusiva
- Texto: Força 5. Zumbis. Defesa: portão 2 + torre 1 + cão 1 + até 3 vigias 4+ + até 2 Munições. Consulte perdas no painel.
- Ilustração: Noite: fila de errantes ao longo da cerca de arame, vista de cima da torre.
- Obrigatório: cerca, fila, vista da torre

**ZC-CER-0003** — Mãos no arame · CER · ×1 · verso V-CER · arte exclusiva
- Texto: Força 6. Zumbis. Defesa: portão 2 + torre 1 + cão 1 + até 3 vigias 4+ + até 2 Munições. Consulte perdas no painel.
- Ilustração: Close de dedos podres enroscados em arame farpado sob luz de lampião.
- Obrigatório: arame farpado, mãos, lampião

**ZC-CER-0004** — Passos no escuro · CER · ×1 · verso V-CER · arte exclusiva
- Texto: Força 4. Zumbis. Defesa: portão 2 + torre 1 + cão 1 + até 3 vigias 4+ + até 2 Munições. Consulte perdas no painel.
- Ilustração: Noite sem lua, só pegadas na lama iluminadas pela lanterna e olhos na mata.
- Obrigatório: pegadas, lanterna, olhos na mata

**ZC-CER-0005** — Cobrança da Ponte · CER · ×1 · verso V-CER · arte exclusiva
- Texto: Força 5. Rivais: ajuste Força por relação: −2 +1; +2 −1. Defesa: portão 2 + torre 1 + cão 1 + até 3 vigias 4+ + até 2 Munições. Consulte perdas no painel.
- Ilustração: Grupo armado de outra comunidade parado no portão, líder com caderno de dívidas, faixas vermelhas no braço.
- Obrigatório: rivais humanos, caderno, faixa vermelha

**ZC-CER-0006** — Caravana hostil · CER · ×1 · verso V-CER · arte exclusiva
- Texto: Força 6. Rivais: podem pagar 4 comida+4 água do estoque antes dos dados para cancelar este cerco. Defesa: portão 2 + torre 1 + cão 1 + até 3 vigias 4+ + até 2 Munições. Consulte perdas no painel.
- Ilustração: Caminhonete com homens armados e luzes altas apontadas para o abrigo, buzina.
- Obrigatório: caminhonete, faróis, rivais humanos

### Evento do dia — Cisterna 0.2 (certificada) (5 cartas, 5 ilustrações exclusivas)

**ZC-EVE-0001** — Bilhete na caixa · EVE · ×1 · verso V-EVE · arte exclusiva
- Texto: Dia 1: leia introdução do capítulo. Mercado ensina primeira rodada sem inimigos.
- Ilustração: Bilhete manuscrito na caixa de correio do abrigo: mapa do Mercado e um aviso.
- Obrigatório: caixa de correio, bilhete, dia 1

**ZC-EVE-0002** — Batidas na cerca · EVE · ×1 · verso V-EVE · arte exclusiva
- Texto: Dia 2: +1 Pressão externa.
- Ilustração: Pedaço de pau batendo na cerca durante a tarde, ninguém visível.
- Obrigatório: cerca, batidas, dia 2

**ZC-EVE-0003** — Barulho no vale · EVE · ×1 · verso V-EVE · arte exclusiva
- Texto: Dia 3: enfileire Cerco de missão Força 4 para esta noite.
- Ilustração: Do alto, o vale com nuvem de poeira se aproximando.
- Obrigatório: vale, poeira, dia 3

**ZC-EVE-0004** — Fumaça no posto · EVE · ×1 · verso V-EVE · arte exclusiva
- Texto: Dia 4: +1 Pressão externa.
- Ilustração: Coluna de fumaça preta subindo do posto de gasolina na saída da cidade.
- Obrigatório: posto, fumaça preta, dia 4

**ZC-EVE-0005** — A última manhã · EVE · ×1 · verso V-EVE · arte exclusiva
- Texto: Dia 5: +1 Pressão; prazo termina após noite.
- Ilustração: Nascer do sol pálido sobre o abrigo, todos de pé, mochilas prontas.
- Obrigatório: amanhecer, grupo reunido, dia 5

### Projeto de obra — Cisterna 0.2 (certificada) (10 cartas, 3 ilustrações exclusivas)

**ZC-PRO-0001** — Barraca → **Projeto: Barraca** · PRO · ×1 · verso V-PRO · arte compartilhada:STR:Barraca
- Texto: 2 Materiais + Lona + 1 trabalho. Um terreno; +2 vagas.
- Ilustração: variação opcional sobre a arte compartilhada — Croqui a lápis de barraca de lona com medidas, sobre foto da lona dobrada.
- Obrigatório: croqui, lona, custo

**ZC-PRO-0002** — Casa simples → **Projeto: Casa simples** · PRO · ×1 · verso V-PRO · arte compartilhada:STR:Casa simples
- Texto: Substitui barraca; 4 Materiais + Madeira + 2 trabalhos. Quatro vagas totais.
- Ilustração: variação opcional sobre a arte compartilhada — Croqui de casinha de madeira com telha de amianto reaproveitada.
- Obrigatório: croqui, telhado

**ZC-PRO-0003** — Enfermaria → **Projeto: Enfermaria** · PRO · ×1 · verso V-PRO · arte compartilhada:STR:Enfermaria
- Texto: 3 Materiais + Kit de instalação + 2 trabalhos. Um terreno; cuidado dispensa Medicamento.
- Ilustração: variação opcional sobre a arte compartilhada — Croqui de cômodo com maca e pia.
- Obrigatório: croqui, maca

**ZC-PRO-0004** — Oficina → **Projeto: Oficina** · PRO · ×1 · verso V-PRO · arte compartilhada:STR:Oficina
- Texto: 3 Materiais + Bancada + 2 trabalhos. Um terreno; habilita reparo de van sem Ferramentas (custo de materiais/trabalho permanece).
- Ilustração: variação opcional sobre a arte compartilhada — Croqui de oficina com bancada e van.
- Obrigatório: croqui, bancada

**ZC-PRO-0005** — Garagem → **Projeto: Garagem** · PRO · ×1 · verso V-PRO · arte compartilhada:STR:Garagem
- Texto: 4 Materiais + Ferramentas + 3 trabalhos. Dois terrenos; +4 cargas de estoque protegido de cerco, escolhidas ao planejar.
- Ilustração: variação opcional sobre a arte compartilhada — Croqui de garagem com portão de enrolar.
- Obrigatório: croqui, portão de enrolar

**ZC-PRO-0006** — Torre → **Projeto: Torre** · PRO · ×1 · verso V-PRO · arte compartilhada:STR:Torre
- Texto: 2 Materiais + Madeira + 2 trabalhos. Perímetro; +1 Defesa ativa.
- Ilustração: variação opcional sobre a arte compartilhada — Croqui de torre de vigia de madeira.
- Obrigatório: croqui, torre

**ZC-PRO-0007** — Horta → **Projeto: Horta** · PRO · ×1 · verso V-PRO · arte compartilhada:STR:Horta
- Texto: 2 Materiais + Sementes + 2 trabalhos. Um terreno; trabalhador produz 4 comida/dia depois de pronta.
- Ilustração: variação opcional sobre a arte compartilhada — Croqui de canteiros com sementes.
- Obrigatório: croqui, canteiros

**ZC-PRO-0008** — Filtro → **Projeto: Filtro** · PRO · ×1 · verso V-PRO · arte exclusiva
- Texto: Etapa A: 1 Material+Conexões+1 trabalho. B: 1 Material+Bomba+1. C: 1 Material+Membrana+2. Max 2 trabalhos/dia; enchimento 2C água ao concluir; depois C/amanhecer.
- Ilustração: Croqui em três etapas (A, B, C) do filtro da cisterna: conexões, bomba, membrana.
- Obrigatório: três etapas, conexões, bomba, membrana

**ZC-PRO-0009** — Expansão → **Projeto: Expansão** · PRO · ×1 · verso V-PRO · arte exclusiva
- Texto: Limpeza adjacente concluída +4 Materiais+2 Madeiras+2 trabalhos. Adicione seis terrenos; máximo uma.
- Ilustração: Grupo com enxadas limpando terreno ao lado do abrigo, estacas com barbante.
- Obrigatório: enxadas, estacas, terreno limpo

**ZC-PRO-0010** — Reparo → **Projeto: Reparo** · PRO · ×1 · verso V-PRO · arte exclusiva
- Texto: 2 Materiais+1 trabalho por estrutura danificada. Volta a funcionar à noite, depois do cerco.
- Ilustração: Mãos martelando tábua nova sobre parede rachada.
- Obrigatório: martelo, tábua nova, rachadura

### Estrutura — Cisterna 0.2 (certificada) (17 cartas, 11 ilustrações exclusivas)

**ZC-STR-0001…ZC-STR-0006** — Barraca · STR · ×6 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Barraca de lona azul armada com cordas, roupa secando, chinelo na porta, quintal de terra.
- Obrigatório: lona azul, varal, 2 vagas

**ZC-STR-0007…ZC-STR-0008** — Casa simples · STR · ×2 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Casinha de madeira com janela de vidro trincado, flores em lata na porta.
- Obrigatório: casa de madeira, 4 vagas

**ZC-STR-0009** — Cozinha · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Fogão a lenha de tijolos com panela de ferro fumegante, cozinheira mexendo.
- Obrigatório: fogão a lenha, panela

**ZC-STR-0010** — Depósito · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Prateleiras de estrado com caixotes etiquetados a giz.
- Obrigatório: prateleiras, giz

**ZC-STR-0011** — Cisterna / filtro · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Caixa-d'água azul sobre base de tijolos com o filtro instalado e torneira pingando.
- Obrigatório: caixa-d'água, filtro, torneira

**ZC-STR-0012** — Enfermaria · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Maca de lona com lençol limpo, varal de soro, lampião, cruz pintada a mão.
- Obrigatório: maca, cruz pintada

**ZC-STR-0013** — Oficina · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Bancada com morsa e ferramentas penduradas em painel de compensado.
- Obrigatório: bancada, painel de ferramentas

**ZC-STR-0014** — Garagem · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Garagem com portão de enrolar meio aberto, van parcialmente visível, caixas trancadas.
- Obrigatório: portão de enrolar, van, estoque protegido

**ZC-STR-0015** — Torre · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Torre de vigia de madeira com escada, vigia com binóculo ao sol.
- Obrigatório: torre, binóculo, +1 Defesa

**ZC-STR-0016** — Horta · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Canteiros de couve, alface e feijão em pneus pintados, regador de lata.
- Obrigatório: canteiros em pneu, regador

**ZC-STR-0017** — Portão · STR · ×1 · verso V-STR · arte exclusiva
- Texto: Coloque no terreno reservado ao concluir. Danificada: vire 90 graus, inativa. Reparo 2 Materiais+1 trabalho. Barracas/casas não são alvos de cerco.
- Ilustração: Portão de chapas soldadas com tranca de cano e correntes.
- Obrigatório: portão soldado, corrente

### Morador resgatado — Cisterna 0.2 (certificada) (8 cartas, 8 ilustrações exclusivas)

**ZC-MOR-0001** — Jana e criança · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Mercado O1; 2 humanos. Jana cozinheira de campo, criança sem trabalho. Pista: protege mochila. Até dia 5. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O1.
- Ilustração: Jana (cozinheira de campo, ZC-HER-0021) abraçando a mochila de mantimentos, criança agarrada à sua perna, corredor do Mercado.
- Obrigatório: retrato de Jana (mesma arte do herói ZC-HER-0021), criança, mochila

**ZC-MOR-0002** — Bia · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Oficina O1; 1 adulta mecânica. Pista: sabe o chassi. Até dia 5. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O1.
- Ilustração: Bia (mecânica, ZC-HER-0023) debaixo de um chassi na Oficina, só o rosto sujo de graxa visível.
- Obrigatório: retrato de Bia (ZC-HER-0023), chassi, graxa

**ZC-MOR-0003** — Vicente e Sol · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Estação O2; 2 adultos, rádio e guia. Pista: estática. Até dia 5. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O2.
- Ilustração: Vicente (operador de rádio, ZC-HER-0024) com fones e Sol (guia, ZC-HER-0019) apontando no mapa, sala de rádio da Estação.
- Obrigatório: Vicente, Sol, rádio, mapa

**ZC-MOR-0004** — Raul e Otávio · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Posto O2; 2 adultos. Pista: negociam chaves. Até dia 5. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O2.
- Ilustração: Raul (caminhoneiro, ZC-HER-0016) e Otávio (porteiro, ZC-HER-0020) negociando um molho de chaves na conveniência do Posto.
- Obrigatório: Raul, Otávio, molho de chaves

**ZC-MOR-0005** — Denise, Miguel e civil · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Hospital O2; 3 humanos, um civil com ferimento 1. Pista: ninguém fica. Até dia 5. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O2.
- Ilustração: Denise (médica, ZC-HER-0017) e Miguel (socorrista, ZC-HER-0022) carregando um civil ferido numa maca no corredor do Hospital.
- Obrigatório: Denise, Miguel, civil ferido, maca

**ZC-MOR-0006** — Samuel, Bruna e criança · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Condomínio O2; 3 humanos. Sementes carga 1 se acolher. Pista: saco fechado. Até dia 5. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O2.
- Ilustração: Samuel (carpinteiro, ZC-HER-0014) e Bruna (agricultora, ZC-HER-0015) com um saco fechado de sementes, criança ao lado, varanda do Condomínio.
- Obrigatório: Samuel, Bruna, criança, saco de sementes

**ZC-MOR-0007** — Aline e cão · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Hospital segunda visita; 1 humana veterinária+1 cão. Pista: examina mordidas. Não duplicar no condomínio. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O2.
- Ilustração: Aline (veterinária, ZC-HER-0013) examinando a pata de um cão no Hospital, lanterna de bolso.
- Obrigatório: Aline, cão, exame

**ZC-MOR-0008** — Hugo · MOR · ×1 · verso V-MOR · arte exclusiva
- Texto: Condomínio segunda visita; 1 adulto eletricista. Pista: traz fios enrolados. Até dia 5. Acolher: vagas ou recepção até +2/duas noites; sorteie uma Intenção por grupo. Ajuda local: 1 comida+1 água/humano. Contato 1 PA em O2.
- Ilustração: Hugo (eletricista, ZC-HER-0018) com rolos de fio no ombro, escada de alumínio, garagem do Condomínio.
- Obrigatório: Hugo, rolos de fio

### Missão — Cisterna 0.2 (certificada) (8 cartas, 2 ilustrações exclusivas)

**ZC-MIS-0001** — Mercado · MIS · ×1 · verso V-MIS · arte compartilhada:LOCAL:Mercado
- Texto: Entregar um lote comida e um água. Revele Ponte na primeira interação O1. Lotes 2 comida e 2 água.
- Ilustração: Fachada de mercadinho de bairro com letreiro caído, carrinhos tombados, lotes de comida e água marcados.
- Obrigatório: mercado, comida, água

**ZC-MIS-0002** — Oficina · MIS · ×1 · verso V-MIS · arte compartilhada:LOCAL:Oficina
- Texto: Entregar Conexões. O1 Conexões+Bateria; O2 três Materiais+Ferramentas+Bancada. Um lote de cada provisão.
- Ilustração: Oficina mecânica com portão de enrolar, bateria e conexões em destaque na bancada.
- Obrigatório: oficina, bateria, conexões

**ZC-MIS-0003** — Estação · MIS · ×1 · verso V-MIS · arte compartilhada:LOCAL:Estação
- Texto: Entregar Bomba+Membrana. O1 Bomba 2 PA+Técnica 6; falha +1 Pressão. O2 Membrana 1 PA e dois lotes água.
- Ilustração: Estação de tratamento de água com tanques, bomba e membrana a recuperar.
- Obrigatório: tanques, bomba, membrana

**ZC-MIS-0004** — Posto · MIS · ×1 · verso V-MIS · arte compartilhada:LOCAL:Posto
- Texto: Recuperar van com Bateria+2 PA+Técnica 6. O1 oito Combustíveis. O2 um lote de cada provisão.
- Ilustração: Posto de gasolina com van de manutenção parada e galões.
- Obrigatório: posto, van, combustível

**ZC-MIS-0005** — Hospital · MIS · ×1 · verso V-MIS · arte compartilhada:LOCAL:Hospital
- Texto: Entregar Kit ou resgatar ferido. O1 Kit+3 Medicamentos. O2 um lote de cada provisão.
- Ilustração: Entrada de hospital regional com ambulância e kit médico.
- Obrigatório: hospital, kit médico, ferido

**ZC-MIS-0006** — Condomínio · MIS · ×1 · verso V-MIS · arte compartilhada:LOCAL:Condomínio
- Texto: Entregar Lona ou limpar expansão: O1 2 PA+Corpo 6, falha Errante em S. O1 duas Lonas+duas Madeiras; O2 um lote de cada provisão.
- Ilustração: Condomínio de casas com lonas e madeiras empilhadas.
- Obrigatório: condomínio, lonas, madeiras

**ZC-MIS-0007** — Contato / encaminhamento · MIS · ×1 · verso V-MIS · arte exclusiva
- Texto: Contato: rota curta+1 rodada sem combate revela Ponte. Encaminhar: expedição rota curta e 1 comida+1 água/passageiro; saem, +1 relação.
- Ilustração: Dois grupos se encontrando numa estrada rural com mãos levantadas, sinal de paz.
- Obrigatório: encontro, mãos levantadas, passageiros

**ZC-MIS-0008** — Segurança final · MIS · ×1 · verso V-MIS · arte exclusiva
- Texto: Dia 5: filtro completo, comida/água para todos, Saúde/Moral >=1. Resolva cercos pendentes sem nova expedição ou produção. Falha abre Evacuação.
- Ilustração: O abrigo inteiro de pé ao amanhecer, filtro funcionando, estoque cheio, portão reforçado.
- Obrigatório: abrigo completo, filtro, amanhecer

### Veículo — Cisterna 0.2 (certificada) (1 cartas, 1 ilustrações exclusivas)

**ZC-VEI-0001** — Van de manutenção · VEI · ×1 · verso V-VEI · arte exclusiva
- Texto: Seis humanos + um cão; 12 cargas; 2 Combustíveis/trecho. Abandonada → incompleta por inspeção → operacional com Bateria e reparo. Danificada: não transporta. Ver manual §11.
- Ilustração: Van branca de prefeitura com faixa laranja, pneus murchos, capô aberto, em pátio de posto.
- Obrigatório: van, faixa laranja, capô aberto

### Ajuda — Cisterna 0.2 (certificada) (8 cartas, 0 ilustrações exclusivas)

**ZC-AJU-0001…ZC-AJU-0002** — Ordem do dia · AJU · ×2 · verso V-AJU · arte compartilhada:diagrama
- Texto: Amanhecer → Planejamento → Expedição → Noite: retorno, um Cerco, trabalhos, refeição, intenções, vencimento → registro.
- Ilustração: Diagrama da sequência do dia sobre quadro de cortiça.
- Obrigatório: sequência numerada

**ZC-AJU-0003…ZC-AJU-0004** — PA · AJU · ×2 · verso V-AJU · arte compartilhada:diagrama
- Texto: Normal 3; fadiga>=2 −1, Fome −1, Sede −1; mínimo 1. Mover/abrir/atacar/buscar/transferir 1; bloqueio com ferramenta 2.
- Ilustração: Diagrama de pontos de ação com ícones.
- Obrigatório: ícones de PA

**ZC-AJU-0005…ZC-AJU-0006** — Retorno · AJU · ×2 · verso V-AJU · arte compartilhada:diagrama
- Texto: Relógio 0–10; curta 1+1, longa 2+2; rodada 1. Segmentos 9–10: +1 fadiga cada, Horda se rodada / Viagem extra se trecho. Emergência perde carga encontrada e objetivo, +1 ferimento e fadiga 3.
- Ilustração: Relógio de 0 a 10 segmentos.
- Obrigatório: relógio 0–10

**ZC-AJU-0007…ZC-AJU-0008** — Reserva não é estoque · AJU · ×2 · verso V-AJU · arte compartilhada:diagrama
- Texto: Saque revela achado. Físico sai da reserva para mochila/chão; entrega vira estoque. Consumido volta só à reserva. Busca usada não se renova.
- Ilustração: Diagrama reserva → mochila → estoque.
- Obrigatório: fluxo de cartas

### Acontecimento de viagem — edição integral (12 cartas, 10 ilustrações exclusivas)

**ZI-ACO-01…ZI-ACO-03** — Viagem tranquila · ACO · ×3 · verso V-ACO · arte exclusiva
- Texto: Sem efeito.
- Ilustração: Coletora atravessando um riacho raso com o cesto cheio, luz de tarde, mata calma.
- Obrigatório: trilha, cesto, calma

**ZI-ACO-04** — Abundância · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: Some 1D6 aos pontos da viagem.
- Ilustração: Pé de goiaba carregado e cardume no remanso; mãos enchendo o saco.
- Obrigatório: fartura, goiabeira, cardume

**ZI-ACO-05** — Descoberta · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: Traga 1 sucata para o estoque.
- Ilustração: Carcaça de trator no meio do pasto com peças aproveitáveis.
- Obrigatório: trator abandonado, peças

**ZI-ACO-06** — Chuva · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: −2 pontos na viagem.
- Ilustração: Temporal no rio, viajante encharcado sob folha de bananeira.
- Obrigatório: temporal, folha de bananeira

**ZI-ACO-07** — Atraso · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: A viagem volta 1 amanhecer depois (uma vez); sorteie de novo na volta.
- Ilustração: Ponte de troncos levada pela cheia; viajante sentado esperando a água baixar.
- Obrigatório: ponte caída, rio cheio, espera

**ZI-ACO-08** — Ferimento · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: O viajante volta com 1 ferimento.
- Ilustração: Tornozelo enfaixado com camisa rasgada, cajado improvisado.
- Obrigatório: faixa improvisada, cajado, vermelho de destaque

**ZI-ACO-09** — Perda de carga · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: Perde metade do que encontrou (arredonda para baixo o que fica).
- Ilustração: Saco rasgado no arame, frutas espalhadas no barranco.
- Obrigatório: saco rasgado, carga espalhada

**ZI-ACO-10** — Equipamento quebrado · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: Gaste 1 sucata do estoque; sem sucata, perde 1 unidade encontrada.
- Ilustração: Vara de pesca partida e anzol perdido na margem.
- Obrigatório: vara quebrada

**ZI-ACO-11** — Zumbis no caminho · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: Role 1D6: 1–2 ferimento e metade da carga; 3–4 perde 1 unidade; 5–6 escapa.
- Ilustração: Errantes saindo do bambuzal, viajante correndo com a carga.
- Obrigatório: bambuzal, errantes, fuga

**ZI-ACO-12** — Pista · ACO · ×1 · verso V-ACO · arte exclusiva
- Texto: +1 pista (só a primeira vez na campanha).
- Ilustração: Panfleto rasgado com frequência de rádio preso num tronco.
- Obrigatório: panfleto, frequência escrita

### Profissão — edição integral (12 cartas, 9 ilustrações exclusivas)

**ZI-PRF-01…ZI-PRF-02** — Caçador · PRF · ×2 · verso V-PRF · arte exclusiva
- Texto: Especialista em: caca, pesca.
- Ilustração: Caçador de chapéu de palha com arco de bambu e varas de pesca nas costas, beira do rio.
- Obrigatório: arco, vara de pesca, ícones caça/pesca

**ZI-PRF-03** — Agricultor · PRF · ×1 · verso V-PRF · arte exclusiva
- Texto: Especialista em: horta, coleta.
- Ilustração: Agricultora de enxada no ombro entre canteiros, mãos de terra.
- Obrigatório: enxada, canteiros, ícones horta/coleta

**ZI-PRF-04** — Cozinheiro · PRF · ×1 · verso V-PRF · arte exclusiva
- Texto: Especialista em: cozinhar.
- Ilustração: Cozinheiro de avental mexendo panelão no fogão a lenha.
- Obrigatório: panelão, avental, ícone cozinhar

**ZI-PRF-05…ZI-PRF-06** — Coletor · PRF · ×2 · verso V-PRF · arte exclusiva
- Texto: Especialista em: coleta, agua, lenha.
- Ilustração: Coletor com cesto de taquara, facão e galão de água, trilha da mata.
- Obrigatório: cesto, facão, galão, ícones coleta/água/lenha

**ZI-PRF-07** — Mecânico · PRF · ×1 · verso V-PRF · arte exclusiva
- Texto: Especialista em: sucata.
- Ilustração: Mecânica com macacão sujo segurando chave de roda, sucata ao fundo.
- Obrigatório: chave de roda, macacão, ícone sucata

**ZI-PRF-08** — Carpinteiro · PRF · ×1 · verso V-PRF · arte exclusiva
- Texto: Especialista em: obra.
- Ilustração: Carpinteiro medindo tábua com trena, lápis atrás da orelha.
- Obrigatório: trena, serrote, ícone obra

**ZI-PRF-09** — Enfermeiro · PRF · ×1 · verso V-PRF · arte exclusiva
- Texto: Especialista em: cuidar.
- Ilustração: Enfermeiro trocando curativo com cuidado, maleta aberta.
- Obrigatório: curativo, maleta, ícone cuidar

**ZI-PRF-10** — Guarda · PRF · ×1 · verso V-PRF · arte exclusiva
- Texto: Especialista em: vigiar.
- Ilustração: Guarda de vigia no alto da torre com binóculo e apito.
- Obrigatório: binóculo, apito, ícone vigiar

**ZI-PRF-11…ZI-PRF-12** — Sobrevivente comum · PRF · ×2 · verso V-PRF · arte exclusiva
- Texto: Especialista em: nenhuma (faz qualquer função com rendimento normal).
- Ilustração: Pessoa comum carregando balde e enxada, roupa remendada; sem ícone de especialidade.
- Obrigatório: balde, sem especialidade

### Estrutura regional — edição integral (7 cartas, 2 ilustrações exclusivas)

**EXP-BLD-01** — Horta · OBR · ×1 · verso V-OBR · arte compartilhada:STR:Horta
- Texto: Custo 2 madeira + 1 sucata; 2 trabalho(s). Modelo abstrato: 2 comida por amanhecer depois de 4 dias.
- Ilustração: variação opcional sobre a arte compartilhada — Horta grande com canteiros elevados de tábua e espantalho de roupa velha.
- Obrigatório: canteiros, espantalho
- Obs.: No acampamento em lotes, vira lotes de horta; a carta EXP-BLD-01 fica para o modelo abstrato.

**EXP-BLD-02** — Oficina · OBR · ×1 · verso V-OBR · arte compartilhada:STR:Oficina
- Texto: Custo 2 madeira + 3 sucata; 3 trabalho(s). Ocupa 1 lote de oficina. Oficina do acampamento (reparos, fabricar munição). Obra pesada: ração de obra.
- Ilustração: variação opcional sobre a arte compartilhada — Oficina de lona e madeira com bancada, morsa e torno manual.
- Obrigatório: bancada, morsa

**EXP-BLD-03** — Enfermaria · OBR · ×1 · verso V-OBR · arte compartilhada:STR:Enfermaria
- Texto: Custo 2 madeira + 2 sucata + 1 remédio; 3 trabalho(s). Ocupa 1 lote de oficina. Cura com remédio; exigida pelo Ambulatório. Obra pesada: ração de obra.
- Ilustração: variação opcional sobre a arte compartilhada — Enfermaria em contêiner com cruz pintada, maca e lampião.
- Obrigatório: contêiner, cruz, maca

**EXP-BLD-04** — Vigia · OBR · ×1 · verso V-OBR · arte compartilhada:STR:Torre
- Texto: Custo 2 madeira + 2 sucata; 2 trabalho(s). Ocupa 1 lote de defesa. Na defesa final, atira 1 por rodada; vigia contra a crise da noite. Obra pesada: ração de obra.
- Ilustração: variação opcional sobre a arte compartilhada — Vigia: torre de bambu e madeira com sino e holofote a pilha.
- Obrigatório: torre, sino, atira na defesa final

**EXP-BLD-05** — Depósito · OBR · ×1 · verso V-OBR · arte compartilhada:STR:Depósito
- Texto: Custo 3 madeira + 2 sucata; 3 trabalho(s). Ocupa 1 lote de estoque. +12 de limite de comida. Obra pesada: ração de obra.
- Ilustração: variação opcional sobre a arte compartilhada — Depósito de alvenaria baixa com prateleiras e portas de grade.
- Obrigatório: prateleiras, porta de grade, +12 comida

**EXP-BLD-06** — Reservatório · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 2 madeira + 3 sucata; 3 trabalho(s). Ocupa 1 lote de agua. +12 de limite de água; água bruta sem ferver. Obra pesada: ração de obra.
- Ilustração: Reservatório: duas caixas-d'água de 1000 L ligadas por cano, bomba manual.
- Obrigatório: caixas-d'água, bomba, +12 água

**EXP-BLD-07** — Alojamento · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 4 madeira + 2 sucata; 3 trabalho(s). Ocupa 1 lote de barraca. 8 camas. Obra pesada: ração de obra.
- Ilustração: Alojamento coletivo de madeira com beliches e redes.
- Obrigatório: beliches, redes, 8 camas

### Obra da Comunidade — edição integral (15 cartas, 13 ilustrações exclusivas)

**ZI-OBR-01** — Coletor de chuva · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 1 madeira + 1 sucata; 1 trabalho(s). Ocupa 1 lote de agua. Chuva: D6 4–5 +2 água, 6 +4.
- Ilustração: Calhas de lona levando chuva para tambores azuis.
- Obrigatório: calha, tambores, chuva

**ZI-OBR-02** — Cozinha · OBR · ×1 · verso V-OBR · arte compartilhada:STR:Cozinha
- Texto: Custo 2 madeira + 1 sucata; 2 trabalho(s). Carne cozida rende 4 porções sem madeira; +1 carne por cozinheiro.
- Ilustração: variação opcional sobre a arte compartilhada — Cozinha comunitária coberta junto à fogueira, mesa longa.
- Obrigatório: fogão, mesa longa

**ZI-OBR-03** — Canteiro · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 2 madeira + 1 sucata; 2 trabalho(s). Modelo abstrato: 2 comida por trabalhador.
- Ilustração: Canteiro simples de pneus.
- Obrigatório: pneus
- Obs.: Só no modelo abstrato; no acampamento em lotes não se imprime.

**ZI-OBR-04** — Cerca ampliada · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 2 madeira; 2 trabalho(s). Modelo abstrato: +3 terreno.
- Ilustração: Cerca de bambu ampliando o terreno.
- Obrigatório: bambu
- Obs.: Só no modelo abstrato; no acampamento em lotes a expansão substitui.

**ZI-OBR-05** — Depósito nível 2 · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 2 madeira + 1 sucata; 2 trabalho(s). +12 de limite de comida (exige Depósito).
- Ilustração: Depósito com mezanino e sacos de grão empilhados.
- Obrigatório: mezanino, +12 comida

**ZI-OBR-06** — Alojamento nível 2 · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 3 madeira + 1 sucata; 2 trabalho(s). +4 camas (exige Alojamento). Obra pesada: ração de obra.
- Ilustração: Alojamento ampliado com segunda ala e varal comprido.
- Obrigatório: segunda ala, +4 camas

**ZI-OBR-07** — Barraca improvisada · OBR · ×1 · verso V-OBR · arte compartilhada:STR:Barraca
- Texto: Custo 2 madeira; 1 trabalho(s). Ocupa 1 lote de barraca. 2 camas; até 2 por lote.
- Ilustração: variação opcional sobre a arte compartilhada — Barraca improvisada de lona e bambu para 2 pessoas, colchonete visível.
- Obrigatório: lona, bambu, 2 camas

**ZI-OBR-08** — Lote de horta · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo sem material; 1 trabalho(s). Ocupa 1 lote de horta. Pronta 3 amanheceres depois; cuidada dá 2 porções.
- Ilustração: Lote de horta recém-plantado: leiras de terra escura, mudas pequenas, regador.
- Obrigatório: leiras, mudas, 2 porções

**ZI-OBR-09** — Expansão 3×3 · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 3 madeira; 3 trabalho(s). Abre o acampamento 3×3 (obra pesada). Obra pesada: ração de obra.
- Ilustração: Mutirão roçando o mato e fincando mourões para abrir o terreno 3×3.
- Obrigatório: roçada, mourões, obra pesada

**ZI-OBR-10** — Expansão 4×4 · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 5 madeira + 2 sucata; 5 trabalho(s). Abre o 4×4; exige Depósito, Oficina ou Vigia (obra pesada). Obra pesada: ração de obra.
- Ilustração: Cerca de mourões e arame circundando o acampamento 4×4, portão novo.
- Obrigatório: perímetro, portão, obra pesada

**ZI-OBR-11** — Composteira · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 1 madeira; 1 trabalho(s). +1 porção por pessoa na horta (exige K-AGR).
- Ilustração: Composteira de paletes com cascas e folhas, minhocas sugeridas.
- Obrigatório: paletes, composto, +1 porção

**ZI-OBR-12** — Defumador · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 2 madeira; 1 trabalho(s). Carne dura +3 noites e cozinha sem madeira (exige K-CON).
- Ilustração: Defumador de tambor com carne pendurada e fumaça fina.
- Obrigatório: tambor, carne defumada

**ZI-OBR-13** — Bancada de ferramentas · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 1 madeira + 2 sucata; 2 trabalho(s). Ocupa 1 lote de oficina. +1 trabalho por pessoa em obra (exige K-FER).
- Ilustração: Bancada de ferramentas organizada com ferramentas recuperadas da Oficina.
- Obrigatório: ferramentas em painel, +1 trabalho

**ZI-OBR-14** — Ambulatório · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 1 madeira + 1 sucata; 2 trabalho(s). +1 pessoa nos cuidados; função remédio: 2 porções → 1 remédio (exige K-SAU e Enfermaria).
- Ilustração: Ambulatório ao lado da enfermaria: prateleira de vidros, alambique de ervas, caderno de fórmulas.
- Obrigatório: vidros, ervas, remédio

**ZI-OBR-15** — Filtro de areia · OBR · ×1 · verso V-OBR · arte exclusiva
- Texto: Custo 1 madeira + 1 sucata; 1 trabalho(s). Ocupa 1 lote de agua. Água bruta vira potável sem ferver (exige K-AGU).
- Ilustração: Filtro de areia em tambores empilhados (areia, carvão, cascalho) com torneira.
- Obrigatório: camadas visíveis, torneira

### Local regional — edição integral (7 cartas, 0 ilustrações exclusivas)

**EXP-LOC-01** — Horta abandonada · LOC · ×1 · verso V-LOC · arte compartilhada:LOCAL:Horta abandonada
- Texto: Distância near; 3 busca(s); saque 2 comida; renovação natural. 1ª busca: conhecimento K-AGR.
- Ilustração: Sítio com horta tomada pelo mato, cerca de bambu caída, poço e galinheiro vazio.
- Obrigatório: cerca de bambu, poço, mato alto

**EXP-LOC-02** — Mercado · LOC · ×1 · verso V-LOC · arte compartilhada:LOCAL:Mercado
- Texto: Distância near; 4 busca(s); saque 2 comida + 1 água; renovação urban. 1ª busca: conhecimento K-CON.
- Ilustração: Mercadinho de bairro de esquina, letreiro caído, prateleiras reviradas, carrinhos no estacionamento; dia claro.
- Obrigatório: letreiro, carrinhos

**EXP-LOC-03** — Oficina · LOC · ×1 · verso V-LOC · arte compartilhada:LOCAL:Oficina
- Texto: Distância medium; 3 busca(s); saque 2 sucata; renovação urban. 1ª busca: conhecimento K-FER.
- Ilustração: Oficina mecânica de portão de enrolar, carros sobre cavaletes, pneus empilhados.
- Obrigatório: portão de enrolar, pneus

**EXP-LOC-04** — Hospital · LOC · ×1 · verso V-LOC · arte compartilhada:LOCAL:Hospital
- Texto: Distância medium; 3 busca(s); saque 2 remédio + 1 água; renovação urban. 1ª busca: conhecimento K-SAU.
- Ilustração: Hospital regional de dois andares com ambulância parada e lençóis nas janelas.
- Obrigatório: ambulância, lençóis nas janelas

**EXP-LOC-05** — Estação · LOC · ×1 · verso V-LOC · arte compartilhada:LOCAL:Estação
- Texto: Distância far; 2 busca(s); saque 2 água + 1 sucata; renovação urban. 1ª busca: conhecimento K-AGU.
- Ilustração: Estação de tratamento de água e ferroviária desativada lado a lado, tanques e trilhos.
- Obrigatório: tanques, trilhos, sala de rádio

**EXP-LOC-06** — Instalação militar · LOC · ×1 · verso V-LOC · arte compartilhada:LOCAL:Instalação militar
- Texto: Distância far; 0 busca(s); saque sem saque comum; renovação urban.
- Ilustração: Portão militar com guarita, galpões verdes, antena de rádio, arame em concertina.
- Obrigatório: guarita, galpões, antena

**EXP-LOC-07** — Posto · LOC · ×1 · verso V-LOC · arte compartilhada:LOCAL:Posto
- Texto: Distância medium; 8 busca(s); saque sem saque comum; renovação urban.
- Ilustração: Posto de gasolina de beira de estrada, bombas antigas, caminhão-tanque parado, conveniência saqueada.
- Obrigatório: bombas, caminhão-tanque

### Crise regional — edição integral (5 cartas, 5 ilustrações exclusivas)

**EXP-CRI-01** — Horta danificada · CRI · ×1 · verso V-CRI · arte exclusiva
- Texto: Alvo: garden; dano 1; perde nada; intervalo 2 dias.
- Ilustração: Horta pisoteada por animais, cerca derrubada, mudas arrancadas.
- Obrigatório: horta danificada

**EXP-CRI-02** — Gafanhotos · CRI · ×1 · verso V-CRI · arte exclusiva
- Texto: Alvo: garden; dano 2; perde 1 comida; intervalo 3 dias.
- Ilustração: Nuvem de gafanhotos sobre os canteiros, pessoas batendo panelas.
- Obrigatório: gafanhotos, panelas

**EXP-CRI-03** — Cupins · CRI · ×1 · verso V-CRI · arte exclusiva
- Texto: Alvo: storage; dano 1; perde 1 madeira; intervalo 3 dias.
- Ilustração: Viga de madeira esfarelando de cupim no depósito.
- Obrigatório: cupim, madeira oca

**EXP-CRI-04** — Água contaminada · CRI · ×1 · verso V-CRI · arte exclusiva
- Texto: Alvo: reservoir; dano 1; perde 2 água; intervalo 3 dias.
- Ilustração: Água turva com espuma no reservatório, criança impedida de beber.
- Obrigatório: água turva, aviso

**EXP-CRI-05** — Estrutura comprometida · CRI · ×1 · verso V-CRI · arte exclusiva
- Texto: Alvo: lodging; dano 2; perde nada; intervalo 2 dias.
- Ilustração: Telhado do alojamento cedendo após temporal, escoras de emergência.
- Obrigatório: telhado cedendo, escoras

### Última Transmissão — edição integral (5 cartas, 5 ilustrações exclusivas)

**EXP-MIS-102** — Decifrar a frequência · UTR · ×1 · verso V-UTR · arte exclusiva
- Texto: Exige: cistern_complete True, clues 2. Custo: 2 clues. Efeito: radio_code.
- Ilustração: Mesa de cozinha com rádio aberto, duas pistas presas com fita, lápis decifrando números.
- Obrigatório: rádio, 2 pistas, números

**EXP-MIS-103** — Cartão na estação · UTR · ×1 · verso V-UTR · arte exclusiva
- Texto: Exige: searches_used 1. Custo: —. Efeito: access_card.
- Ilustração: Cartão de acesso militar caído entre trilhos da Estação, sol rasante.
- Obrigatório: cartão de acesso, trilhos

**EXP-MIS-104** — Acesso militar · UTR · ×1 · verso V-UTR · arte exclusiva
- Texto: Exige: radio_code True, access_card True, vehicle True, fuel_round_trip 12. Custo: 12 combustível. Efeito: military_access.
- Ilustração: Van chegando ao portão da Instalação militar, leitor de cartão com luz verde.
- Obrigatório: van, portão militar, combustível

**EXP-MIS-105** — Transporte do transmissor · UTR · ×1 · verso V-UTR · arte exclusiva
- Texto: Exige: military_access True, cargo_capacity 1. Custo: 1 actions. Efeito: transmitter.
- Ilustração: Heróis carregando o transmissor em caixa reforçada pela rampa do galpão militar.
- Obrigatório: transmissor, caixa reforçada

**EXP-MIS-106** — Defesa da última transmissão · UTR · ×1 · verso V-UTR · arte exclusiva
- Texto: Exige: transmitter True, final_defense True. Custo: —. Efeito: free_survival.
- Ilustração: Defesa final ao entardecer: acampamento iluminado, antena erguida, heróis na cerca e a Vigia atirando.
- Obrigatório: antena, defesa, Vigia, único entardecer da edição

### Referência da comunidade — edição integral (8 cartas, 0 ilustrações exclusivas)

**ZI-REF-01** — Bagagem do resgatado · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: D6 ao acolher um adulto: 1 nada; 2 1 comida; 3 1 comida + 1 água; 4 2 comida; 5 1 madeira + 1 sucata; 6 1 remédio + 1 comida.
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

**ZI-REF-02** — Viagem automática · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: 1–3 dias; pontos = (D6 + especialista + cão) × dias − dias sem ração; conversão por atividade; 1 carta de acontecimento (+1 em viagem longa ou perigosa).
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

**ZI-REF-03** — Comida e água · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: Cada pessoa: 1 porção de comida e 1 de água por noite. Carne cozida rende 4 porções; fruta dá água a cada 2.
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

**ZI-REF-04** — Tempo e coletor · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: D6 por amanhecer: 4–6 chove. Coletor: 4–5 +2 água, 6 +4.
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

**ZI-REF-05** — Chegadas · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: Dias 4 e 10, D6: 1–2 adulto; 3–4 adulto + criança com barraca; 5 dois adultos + criança com barraca familiar; 6 ninguém. Recusar: Crise +1.
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

**ZI-REF-06** — Horta por lotes · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: Pessoa cuida de 2 lotes (agricultor 4); lote cuidado dá 2 porções; dia seco: 1 água a cada 2 lotes; D6 = 1: −1 porção.
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

**ZI-REF-07** — Crise · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: Falta para até metade: +1; mais: +2; todos servidos: −1 (−2 com reserva). 4 obras pesadas param; 7 ninguém recupera; 10 colapso.
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

**ZI-REF-08** — Obras e ração · REF · ×1 · verso V-REF · arte compartilhada:diagrama
- Texto: Obra pesada: 1 porção por pessoa no dia. Barraca e horta são leves. Expansão 3×3: 3 madeira, 3 trabalhos; 4×4: 5 madeira + 2 sucata, 5 trabalhos.
- Ilustração: Sem ilustração: ícones e diagrama sobre prancheta.
- Obrigatório: ícones

### Conhecimento — edição integral (5 cartas, 5 ilustrações exclusivas)

**K-AGR** — Caderno de cultivo · CON · ×1 · verso V-CON · arte exclusiva
- Texto: 1ª busca em EXP-LOC-01. Libera a obra Composteira.
- Ilustração: Caderno de cultivo com desenhos de leiras e calendário de plantio, terra entre as páginas.
- Obrigatório: caderno, desenho de leiras

**K-CON** — Manual de conservas · CON · ×1 · verso V-CON · arte exclusiva
- Texto: 1ª busca em EXP-LOC-02. Libera a obra Defumador.
- Ilustração: Manual de conservas com receita de defumação, fotos de potes.
- Obrigatório: manual, potes

**K-FER** — Catálogo de ferramentas · CON · ×1 · verso V-CON · arte exclusiva
- Texto: 1ª busca em EXP-LOC-03. Libera a obra Bancada de ferramentas.
- Ilustração: Catálogo de ferramentas com páginas marcadas e anotações.
- Obrigatório: catálogo, marcações

**K-SAU** — Fórmulas de manipulação · CON · ×1 · verso V-CON · arte exclusiva
- Texto: 1ª busca em EXP-LOC-04. Libera a obra Ambulatório.
- Ilustração: Fichário de farmácia de manipulação com fórmulas fictícias e etiquetas de ervas (sem instruções reais).
- Obrigatório: fichário, etiquetas de ervas, fórmulas fictícias

**K-AGU** — Esquema de filtro de areia · CON · ×1 · verso V-CON · arte exclusiva
- Texto: 1ª busca em EXP-LOC-05. Libera a obra Filtro de areia.
- Ilustração: Esquema técnico de filtro de areia em folha quadriculada, camadas coloridas a lápis.
- Obrigatório: esquema, camadas

## 5. Pessoas (25 retratos)

| Id | Nome | Profissão | Uso | Retrato |
|---|---|---|---|---|
| ZC-HER-0001 | Lia | agente comunitária de saúde | herói inicial, regional | Lia, ~40 anos, mulher negra de tranças presas, colete de agente de saúde desbotado, prancheta e mochila de primeiros socorros; olhar firme e acolhedor. |
| ZC-HER-0002 | Ivo | vigilante | herói inicial, regional | Ivo, ~45 anos, homem pardo corpulento, careca, uniforme de vigilante sem distintivo, cassetete trocado por pé de cabra, barba grisalha. |
| ZC-HER-0003 | Mara | técnica de enfermagem | herói inicial, regional | Mara, ~30 anos, mulher branca de cabelo curto castanho, jaleco cortado na manga, estetoscópio, olheiras. |
| ZC-HER-0004 | Caio | entregador ciclista | herói inicial, regional | Caio, ~22 anos, rapaz negro magro, capacete de ciclista riscado, bag térmica de entregas nas costas, tênis de corrida. |
| ZC-HER-0005 | Nara | técnica de saneamento | herói inicial, regional | Nara, ~35 anos, mulher indígena de cabelo liso preso, botas de borracha, macacão de saneamento, chave de registro. |
| ZC-HER-0006 | Bento | pedreiro | herói inicial, regional | Bento, ~55 anos, homem branco queimado de sol, chapéu de pedreiro, colher de pedreiro no cinto, mãos grossas. |
| ZC-HER-0007 | Duda | técnica em eletrônica | herói inicial, regional | Duda, ~26 anos, pessoa não binária de cabelo raspado nas laterais, óculos remendados, multímetro e fios no bolso. |
| ZC-HER-0008 | Rosa | cozinheira escolar | herói inicial, regional | Rosa, ~60 anos, mulher parda baixa de touca e avental de cozinha escolar, concha de alumínio, sorriso cansado. |
| ZC-HER-0009 | Joel | bombeiro civil | herói inicial, regional | Joel, ~38 anos, homem negro alto, jaqueta de bombeiro civil com faixa refletiva, machadinha. |
| ZC-HER-0010 | Yumi | técnica de laboratório | herói inicial, regional | Yumi, ~33 anos, mulher nipo-brasileira de franja, avental de laboratório manchado, caixa térmica com amostras. |
| ZC-HER-0011 | Téo | encanador | herói inicial, especialista EXP-NPC-01 | Téo, ~48 anos, homem branco de bigode, encanador de bermuda e camiseta de loja de material, chave grifo no ombro. |
| ZC-HER-0012 | Célia | professora | herói inicial, especialista EXP-NPC-02 | Célia, ~52 anos, professora negra de óculos de grau e cabelo crespo grisalho, cadernos sob o braço, rádio portátil. |
| ZC-HER-0013 | Aline | veterinária | herói resgatável, especialista EXP-NPC-03 | Aline, ~29 anos, veterinária branca de rabo de cavalo ruivo, colete com bolsos, coleira e lanterna de bolso. |
| ZC-HER-0014 | Samuel | carpinteiro | herói resgatável, especialista EXP-NPC-04 | Samuel, ~50 anos, carpinteiro pardo de barba, lápis na orelha, serrote nas costas. |
| ZC-HER-0015 | Bruna | agricultora | herói resgatável, especialista EXP-NPC-05 | Bruna, ~36 anos, agricultora negra de chapéu de palha e lenço, saco de sementes, mãos de terra. |
| ZC-HER-0016 | Raul | caminhoneiro | herói resgatável, especialista EXP-NPC-06 | Raul, ~58 anos, caminhoneiro branco barrigudo de boné de transportadora, camisa aberta, chaves no cinto. |
| ZC-HER-0017 | Denise | médica | herói resgatável, especialista EXP-NPC-07 | Denise, ~46 anos, médica parda de cabelo curto grisalho, jaleco sujo, crachá de hospital, expressão exausta. |
| ZC-HER-0018 | Hugo | eletricista | herói resgatável, especialista EXP-NPC-08 | Hugo, ~40 anos, eletricista negro de capacete branco, cinto de ferramentas, rolos de fio. |
| ZC-HER-0019 | Sol | guia | herói resgatável, especialista EXP-NPC-09 | Sol, ~24 anos, guia indígena de cabelo longo, mochila de trilha, bússola e facão. |
| ZC-HER-0020 | Otávio | porteiro | herói resgatável, especialista EXP-NPC-10 | Otávio, ~65 anos, porteiro branco de cabelo branco penteado, camisa social gasta, molho de chaves e rádio HT. |
| ZC-HER-0021 | Jana | cozinheira de campo | herói resgatável, especialista EXP-NPC-11 | Jana, ~34 anos, cozinheira de campo parda de cabelo cacheado preso em lenço, avental de lona, mochila de mantimentos. |
| ZC-HER-0022 | Miguel | socorrista | herói resgatável, especialista EXP-NPC-12 | Miguel, ~27 anos, socorrista branco de colete laranja, prancha rígida no ombro. |
| ZC-HER-0023 | Bia | mecânica | herói resgatável, especialista EXP-NPC-13 | Bia, ~31 anos, mecânica negra de macacão com mangas amarradas na cintura, rosto com graxa, chave de roda. |
| ZC-HER-0024 | Vicente | operador de rádio | herói resgatável, especialista EXP-NPC-14 | Vicente, ~70 anos, operador de rádio branco magro, fones antigos, cardigã, caderno de frequências. |
| EXP-NPC-15 | Lúcia | zeladora de escola | só especialista | Lúcia, ~44 anos, zeladora de manutenção parda de cabelo curto, uniforme de prefeitura, caixa de ferramentas e lanterna de cabeça. |

## 6. Inimigos

| Id | Nome | Ilustrações | Descrição |
|---|---|---|---|
| slow | Errante | 4 | Morto-vivo lento de roupa comum rasgada (camisa de time, chinelo), pele acinzentada, andar arrastado; 4 variações (homem, mulher, idoso, trabalhador de uniforme). |
| runner | Corredor | 2 | Morto-vivo magro e ágil, corpo inclinado para a frente, roupas esportivas rasgadas; 2 variações. |
| brute | Bruto | 1 | Morto-vivo enorme, de macacão de frigorífico ou colete de segurança, ombros largos, pedaço de grade preso ao braço. |
| rivais | Rivais humanos | 1 | Grupo armado de outra comunidade com faixas vermelhas no braço (Cerco: Cobrança da Ponte, Caravana hostil). |

## 7. Locais e mapas

| Local | Arte-chave |
|---|---|
| Mercado | Mercadinho de bairro de esquina, letreiro caído, prateleiras reviradas, carrinhos no estacionamento; dia claro. |
| Hospital | Hospital regional de dois andares com ambulância parada e lençóis nas janelas. |
| Oficina | Oficina mecânica de portão de enrolar, carros sobre cavaletes, pneus empilhados. |
| Posto | Posto de gasolina de beira de estrada, bombas antigas, caminhão-tanque parado, conveniência saqueada. |
| Condomínio | Condomínio de casas geminadas com muro alto e guarita vazia. |
| Estação | Estação de tratamento de água e ferroviária desativada lado a lado, tanques e trilhos. |
| Horta abandonada | Sítio com horta tomada pelo mato, cerca de bambu caída, poço e galinheiro vazio. |
| Instalação militar | Portão militar com guarita, galpões verdes, antena de rádio, arame em concertina. |
| Acampamento | Clareira da comunidade: barracas azuis, fogueira, varal, primeiras leiras, mato em volta; usado no tabuleiro e na defesa final. |

| Mapa | Local | Uso |
|---|---|---|
| ZC-MAP-0001 | Mercado | Cisterna 0.2 (certificado) |
| ZC-MAP-0002 | Hospital | Cisterna 0.2 (certificado) |
| ZC-MAP-0003 | Oficina | Cisterna 0.2 (certificado) |
| ZC-MAP-0004 | Posto | Cisterna 0.2 (certificado) |
| ZC-MAP-0005 | Condomínio | Cisterna 0.2 (certificado) |
| ZC-MAP-0006 | Estação | Cisterna 0.2 (certificado) |
| market_intro | Mercado | regional |
| hospital_02 | Hospital | regional |
| workshop_02 | Oficina | regional |
| gas_station_02 | Posto | regional (tanque do caminhão na zona 14) |
| condominium_02 | Condomínio | regional |
| station_02 | Estação | regional |
| military_installation | Instalação militar | regional (transmissor) |
| garden_edge_01 | Horta abandonada | regional (4×4 zonas) |
| camp_final | Acampamento | defesa final |

Vista isométrica diurna, zonas numeradas legíveis, portas (comum, bloqueada, cerca) e pontos de busca/objetivo como ícones sobre a arte; o mesmo local da Cisterna e do regional pode dividir a pintura de base e mudar só a camada de zonas.

## 8. Construções (peças de lote) e tabuleiros

Peças de lote usam a arte da carta de estrutura correspondente (data/art/integral.json#estruturas) em recorte quadrado 40 × 40 mm, frente 'pronta' e verso 'em obra' (estacas e barbante).

- Barraca familiar: Barraca familiar de camping de 4 lugares, desbotada, com varal e cadeiras de praia.
- tabuleiro_acampamento: 4×4 lotes de 45 mm em terra batida vista de cima; cada lote com os símbolos de categoria; fogueira e estoque inicial na borda; 2 tiras de mato em L para os lotes fechados.
- painel_abrigo: Duas folhas: trilhas de comida, água, madeira, metal, carne, moradores/camas, Crise 0–10 (gradiente creme → vermelho) e dias 1–25 (dia 25 'a frequência cala'); fundo de prancheta.
- tabuleiro_entorno: Mapa ilustrado de floresta, rio e ruínas com as reservas de caça, peixe, madeira, frutas e sucata.

## 9. Marcadores

| Marcador | Qtd. | Arte |
|---|---|---|
| hero | 24 | Retrato em círculo de cada herói (mesma arte da ficha), borda na cor do jogador. |
| enemy | 24 | Silhueta Errante/Corredor/Bruto numerada E01–E24 (fichas do motor tático). |
| Errante | 12 | Ficha redonda com a arte do Errante. |
| Corredor | 6 | Ficha redonda com a arte do Corredor. |
| Bruto | 6 | Ficha redonda maior com a arte do Bruto. |
| Porta | 12 | Porta de madeira/aço em vista isométrica (aberta no verso). |
| Bloqueio | 6 | Móveis empilhados bloqueando passagem. |
| Busca | 12 | Ícone de lupa sobre caixote; verso 'usada'. |
| Fome | 12 | Prato vazio (vermelho de destaque). |
| Sede | 12 | Copo vazio rachado. |
| Dano | 8 | Gota/rasgo vermelho. |
| Verificado | 6 | Prancheta com visto. |
| numeros_1_4 | 56 | Fichas numéricas 1 (20), 2 (12), 3 (12), 4 (12) para cursores. |
| Relógio | 1 | Ponteiro de relógio de 0–10. |
| Pressão | 1 | Marcador de pressão externa. |
| marcadores_integral | ver print_inventory.json#tokens_new | Trilhas (8), ficha LIMITE (2), Crise (1, vermelho), cubos de obra (6), peões de trabalhador (12), viajantes (6), armadilhas (2). |

## 10. Versos

| Verso | Desenho |
|---|---|
| V-VIN | Vínculo: foto rasgada de família presa por fita adesiva sobre madeira escura. |
| V-INT | Intenção (oculta): rosto na sombra atrás de grade de portão; idêntico para as 4 intenções. |
| V-REC | Recurso: caixote de feira de madeira com estêncil 'ESTOQUE'. |
| V-PEC | Peça de missão: chapa metálica com parafusos e etiqueta de patrimônio. |
| V-EQU | Equipamento: lona verde com ferramentas em silhueta. |
| V-SAQ | Saque: faixa com o nome do local sobre fundo do mapa daquele local (6 versões: Mercado, Hospital, Oficina, Posto, Condomínio, Estação). |
| V-VIA | Viagem: estrada de terra entre pasto alto, placa de quilometragem. |
| V-HOR | Horda: mãos e silhuetas contra portão, tons ferrugem. |
| V-CER | Cerco: cerca de arame à noite com lanterna. |
| V-EVE | Evento do dia: calendário de parede marcado a caneta. |
| V-PRO | Projeto de obra: papel de pão com croqui a lápis. |
| V-STR | Estrutura: tábua com régua de pedreiro e prumo. |
| V-MOR | Morador: crachá de abrigo com cordão. |
| V-MIS | Missão: mapa rodoviário dobrado com círculo vermelho. |
| V-VEI | Veículo: chave de van com chaveiro de oficina. |
| V-AJU | Ajuda: quadro de avisos de cortiça. |
| V-ACO | Acontecimento de viagem automática: trilha na mata com pegadas. |
| V-PRF | Profissão (sorteio oculto): luvas de trabalho sobre bancada; igual para as 12. |
| V-OBR | Obra regional: lote de terra com estacas e barbante. |
| V-LOC | Local regional: placa de estrada com km e seta. |
| V-CRI | Crise regional: céu de tempestade sobre plantação. |
| V-UTR | Última Transmissão: rádio de ondas curtas com ponteiro aceso. |
| V-REF | Referência da comunidade: prancheta com folha de controle. |
| V-CON | Conhecimento: caderno de capa dura com fita adesiva. |

V-SAQ tem 6 variações (uma por local).

## 11. Molduras

- **padrao:** 63 × 88 mm; moldura 3 mm; ilustração 57 × 44 mm; caixa de texto creme 57 × 30 mm; sangria 3 mm fora do corte.
- **recurso:** Ilustração maior (57 × 52 mm) e cursor de porções 4/3/2/1 na borda direita (Conserva, Água, Carne).
- **saque:** Arte do recurso (compartilhada com REC) + faixa superior com o local; texto curto.
- **referencia:** Sem ilustração grande: ícones e diagrama; frente e verso podem ser texto.
