import re
from urllib.parse import quote


def montar_link_whatsapp(treino, exercicios):
    telefone = re.sub(r'\D', '', treino.aluno.telefone or '')
    if len(telefone) in (10, 11):
        telefone = '55' + telefone      # DDD + número: acrescenta o código do Brasil

    linhas = [
        f'Olá, {treino.aluno.nome}! Seu treino *{treino.nome_treino}* está pronto.',
        f'Período: {treino.data_inicio:%d/%m/%Y} a {treino.data_fim:%d/%m/%Y}',
        '',
    ]

    for item in exercicios:
        linhas.append(
            f'• {item.exercicio.nome}: {item.series}x{item.repeticoes}'
            f' | descanso {item.descanso} min | {item.peso_atual:g} kg'
        )

    linhas += ['', 'Bons treinos! 💪']

    return f'https://wa.me/{telefone}?text={quote(chr(10).join(linhas))}'