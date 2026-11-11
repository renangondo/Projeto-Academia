from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

AZUL = colors.HexColor('#2563eb')
AZUL_CLARO = colors.HexColor('#eff6ff')
CINZA = colors.HexColor('#64748b')


def _rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(CINZA)
    canvas.drawString(2 * cm, 1.2 * cm, 'RGN - Sistema de Gerenciamento de Treino')
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f'Página {doc.page}')
    canvas.restoreState()


def gerar_pdf_treino(treino, exercicios):
    exercicios = list(exercicios)
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        title=f'Treino {treino.nome_treino}',
    )

    base = getSampleStyleSheet()['Normal']
    titulo = ParagraphStyle('titulo', parent=base, fontName='Helvetica-Bold',
                            fontSize=22, leading=26, textColor=AZUL)
    subtitulo = ParagraphStyle('subtitulo', parent=base, fontSize=9, textColor=CINZA,
                               spaceBefore=4, spaceAfter=16)
    rotulo = ParagraphStyle('rotulo', parent=base, fontName='Helvetica-Bold', fontSize=10)
    texto = ParagraphStyle('texto', parent=base, fontSize=10, leading=13)
    cabecalho = ParagraphStyle('cabecalho', parent=base, fontName='Helvetica-Bold',
                               fontSize=9, textColor=colors.white)
    celula = ParagraphStyle('celula', parent=base, fontSize=9, leading=11)

    professor = treino.aluno.professor or treino.cadastrado_por
    criado = timezone.localtime(treino.cadastrado_em).strftime('%d/%m/%Y')
    atualizado = timezone.localtime(treino.atualizado_em).strftime('%d/%m/%Y %H:%M')

    elementos = [
        Paragraph('Ficha de Treino', titulo),
        Paragraph(f'Criado em {criado} | Atualizado em {atualizado}', subtitulo),
    ]

    dados = [
        ('Aluno', treino.aluno.nome),
        ('Professor', professor.nome),
        ('Treino', treino.nome_treino),
        ('Período', f'{treino.data_inicio:%d/%m/%Y} a {treino.data_fim:%d/%m/%Y}'),
        ('Objetivo', treino.descricao),
    ]
    info = Table(
        [[Paragraph(r, rotulo), Paragraph(escape(v), texto)] for r, v in dados],
        colWidths=[3 * cm, 14 * cm],
    )
    info.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elementos += [info, Spacer(1, 18)]

    linhas = [[Paragraph(t, cabecalho) for t in
               ('Exercício', 'Categoria', 'Séries', 'Repetições', 'Descanso', 'Carga')]]

    for item in exercicios:
        linhas.append([
            Paragraph(escape(item.exercicio.nome), celula),
            Paragraph(escape(item.exercicio.categoria.nome), celula),
            str(item.series),
            str(item.repeticoes),
            f'{item.descanso} min',
            f'{item.peso_atual:g} kg',
        ])

    if not exercicios:
        linhas.append([Paragraph('Nenhum exercício cadastrado neste treino.', celula), '', '', '', '', ''])

    tabela = Table(
        linhas,
        colWidths=[5.2 * cm, 3.2 * cm, 1.8 * cm, 2.4 * cm, 2.2 * cm, 2.2 * cm],
        repeatRows=1,
    )
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, AZUL_CLARO]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 1), (-1, -1), 'CENTER'),
        ('FONTSIZE', (2, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabela)

    doc.build(elementos, onFirstPage=_rodape, onLaterPages=_rodape)
    return buffer.getvalue()