# Checkpoint

Base: c2e66fd; branch: arte/mercado-amostra-ilustrada. Variante isolada em samples/mercado-b-pos-apocaliptico. Mercado B refinado e todas as edições anteriores preservados.

Concluído: piloto R2C1 inspecionado; nove seções editadas; seis reparos de móveis inteiros; correção ampliada dos caixas; dois reparos de acesso; composição 175 ppi; interface vetorial; quatro A4; prova comparativa de dois recortes 100 × 100 mm; capturas, diagnóstico em cinza, manifesto e revisão de conectores.

Reproduzir, na raiz do repositório:

```sh
python samples/mercado-b-pos-apocaliptico/fontes/compose.py
python samples/mercado-b-pos-apocaliptico/fontes/build.py
python samples/mercado-b-pos-apocaliptico/fontes/proofs.py
python samples/mercado-b-pos-apocaliptico/fontes/validate.py
```

Dependências locais já usadas: Python, Pillow, NumPy, ReportLab, PyMuPDF e DejaVu Sans. O processo reaproveita as imagens nativas salvas; não precisa chamar image_gen para reconstruir PDFs. A comparação consulta o PDF da base em samples/mercado-b-refinado. Marcadores existentes são lidos somente para a simulação.

Nenhuma aplicação aos outros destinos. Aguardam avaliação do proprietário e futura prova doméstica. Se uma revisão artística for pedida, editar só a seção/reparo afetado, preservar sua tentativa, conferir conectores próximos, reconstruir e renderizar. Não substituir automaticamente a edição distribuída.
