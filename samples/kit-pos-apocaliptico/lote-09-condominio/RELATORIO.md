# Lote 09 — condomínio, prova artística

O condomínio foi recomposto como um conjunto residencial contínuo: estacionamento e portaria, salão usado pelos moradores, escadaria, cozinha improvisada, pátio ajardinado e áreas de serviço. Desgaste, vidros e mobiliário seguem o Mercado B pós-apocalíptico. O mapa anterior e o pacote distribuído continuam intactos. Esta pasta é uma **prova opcional**, ainda sem impressão física.

- [Mapa em quatro A4 paisagem](CONDOMINIO_4_A4.pdf), 100%, corte de 277 × 190 mm e montagem de 554 × 380 mm.
- [Mapa remontado com geometria](CONDOMINIO_COM_GEOMETRIA.png) · [arte sem interface](CONDOMINIO_SEM_INTERFACE.png) · [comparação anterior → prova](COMPARACAO_B_ANTES_DEPOIS.jpg).
- [Prova de detalhe de 100 mm](DETALHE_100MM_A4.pdf) · [comparação no mesmo tamanho](COMPARACAO_100MM_A4.pdf).
- [Contato das 21 conexões](provas/CONEXOES_21.jpg) · [quatro páginas](provas/CONTATO_4_A4.jpg) · [cinza](provas/CONDOMINIO_CINZA.png) · [ocupação digital](provas/OCUPACAO_A4.pdf).

A fonte funcional é `content/production/geometry_0.6.json`, ID ZC-MAP-0005: 16 zonas, 21 conexões, cinco portas e bloqueio inicial 9–13; entrada Z1, buscas Z5/Z12, objetivos Z7/Z14 e surgimento Z16. A composição respeita a planta funcional. Sete edições localizadas liberaram os conectores 1–5, 3–4, 5–6, 7–8, 8–12, 11–15 e 12–16. A porta 9–13 permanece bloqueada conforme a regra. Nenhum móvel decorativo muda a circulação.

As nove reconstruções nativas e sete reparos formam uma arte de 3817 × 2618 px para 554 × 380 mm: **175,0 ppi efetivos**. A composição global pequena foi apenas guia de posicionamento, nunca ampliada para o PDF. Dimensões individuais estão em `fontes/resolucao.json`. Geometria, textos e símbolos são vetoriais. `VERIFICACOES.json` registra A4, fontes incorporadas e correspondência com a fonte funcional.

As quatro páginas foram renderizadas e inspecionadas digitalmente, incluindo junções, todas as conexões, detalhe físico simulado e cinza. Persistem pequenas diferenças de textura em alguns reparos e faces laterais estilizadas em móveis; o resultado requer avaliação artística. **Não houve impressão física, montagem ou playtest humano.** Não substituir o arquivo da edição distribuída até essa validação.

Reconstrução pela raiz do repositório: `python samples/kit-pos-apocaliptico/lote-09-condominio/fontes/compose.py`, depois `build.py` e `diagnostics.py` da mesma pasta. Requer Pillow, NumPy, ReportLab e PyMuPDF.
