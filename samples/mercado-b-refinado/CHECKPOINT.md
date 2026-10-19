# Checkpoint — mercado B refinado

Base: 9d08b2f. Branch de trabalho: arte/mercado-amostra-ilustrada. Entrega isolada em samples/mercado-b-refinado. Candidata anterior preservada.

Concluídos: teste de duas seções vizinhas; nove seções nativas; correção de junção; oito reparos; liberação Z15–Z16/4–8/8–12; integração vetorial; quatro A4; prova 100 mm; comparações e inspeção das 21 conexões; manifesto de resolução.

Reprodução, a partir da raiz do repositório:

```sh
python samples/mercado-b-refinado/fontes/compose.py
python samples/mercado-b-refinado/fontes/build.py
python samples/mercado-b-refinado/fontes/proofs.py
```

Dependências: Python, Pillow, NumPy, PyMuPDF, ReportLab e fontes DejaVu Sans em /usr/share/fonts/truetype/dejavu. A geração integrada não precisa ser repetida: as saídas nativas estão em originais/. JSONs definem todos os recortes físicos e o compositor mantém apenas redução de imagem.

A composição de referência da candidata anterior está em samples/mercado-ilustrado. proofs.py usa também seu PDF para antes/depois. build.py consulta os marcadores existentes somente para simulação digital.

Pendências: aprovação visual do proprietário, prova física, pequenas faces laterais periféricas e variações de piso descritas no relatório. Não aplicar aos outros destinos sem avaliação. Para uma correção futura, editar somente o reparo nativo correspondente com image_gen, preservar a tentativa, reconstruir e conferir conectores locais. Não substituir o mercado anterior automaticamente.
