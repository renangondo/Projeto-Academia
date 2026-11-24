import re
from urllib.parse import quote


def normalizar_telefone(telefone):
    """Devolve só dígitos com DDI 55, ou None se o número for inválido."""
    digitos = re.sub(r'\D', '', telefone or '')
    if len(digitos) in (10, 11):
        return '55' + digitos
    if len(digitos) in (12, 13) and digitos.startswith('55'):
        return digitos
    return None


def montar_mensagem(treino):
    linhas = [f'Olá, {treino.aluno.nome}! Segue o seu treino:', '']  # AJUSTAR: nome do campo
    linhas.append(f'*{treino.nome}*')                                   # AJUSTAR: nome do treino
    linhas.append('')
    for item in treino.exerciciotreino_set.select_related('exercicio'):  # AJUSTAR: related_name
        linhas.append(
            f'• {item.exercicio.nome}: {item.series}x{item.repeticoes}'  # AJUSTAR: campos
        )
    linhas.append('')
    linhas.append('Bom treino! 💪')
    return '\n'.join(linhas)


def montar_link_whatsapp(treino):
    numero = normalizar_telefone(treino.aluno.telefone)  # AJUSTAR: campo do telefone
    if not numero:
        return None
    return f'https://wa.me/{numero}?text={quote(montar_mensagem(treino))}'