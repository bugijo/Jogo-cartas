# Reconstruir os tabuleiros 0.6

Para imprimir, não é necessário executar código: use DOWNLOADS_0.6.md.

Para editar a arte, extraia FONTES_CODIGO_ARTE. O catálogo geométrico e os cenários estão em content/production; as imagens originais ficam em assets/v0.6 e os originais reutilizados em assets/v0.5. SVGZ contém a geometria funcional separada. Não regrave as fontes mecânicas.

Python 3, requirements.txt e fontes DejaVu Sans nos caminhos de src/build_boards06.py. Para gerar somente mapas, sem cartas:

    python src/build_boards06.py --maps-only

Para reconstruir o kit completo e todas as comparações, extraia também TODAS as partes FONTES_BASE05 no mesmo diretório, mantendo os caminhos. São PDFs anteriores, necessários à cópia byte a byte e às provas. Depois:

    python src/build_boards06.py
    python src/validate_boards06.py
    python src/proof_boards06.py
    python -m unittest discover -s tests -p test_boards06.py
    python src/document_boards06.py
    python src/package_boards06.py

O build 0.6 não executa geradores antigos: copia os componentes preservados e gera apenas mapas e montagens. Os módulos principais usam pixels nativos, recortados sem reamostragem na incorporação ao PDF. As miniaturas de ambientação dos diagramas são derivadas a 200 ppi; geometria e texto são sobrepostos em vetor.

Não confundir mapas principais A4 com PDFs de cena global e plantas funcionais: estes são fontes/provas de 554×380 mm, não uma folha A4 reduzida para jogar.

A conferência digital não substitui calibração da impressora, prova de recorte e montagem física. Nada continua em segundo plano após a entrega.
