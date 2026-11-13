CAMPOS_VARIACAO = ['peso', 'cintura', 'quadril', 'braco_direito', 'braco_esquerdo',
                   'coxa_direita', 'coxa_esquerda', 'panturrilha_direita',
                   'panturrilha_esquerda', 'peito']


def calcular_variacoes(atual, anterior):
    """Diferença de cada medida entre as duas últimas medições."""
    variacoes = {}

    if anterior is None:
        return variacoes

    for campo in CAMPOS_VARIACAO:
        diferenca = round(getattr(atual, campo) - getattr(anterior, campo), 1)

        if diferenca > 0:
            sentido = 'subiu'
        elif diferenca < 0:
            sentido = 'desceu'
        else:
            sentido = 'igual'

        variacoes[campo] = {'valor': abs(diferenca), 'sentido': sentido}

    return variacoes



def calcular_imc(peso, altura):
    if not peso or not altura:
        return None
    if altura > 3:          # altura digitada em cm (ex.: 175)
        altura = altura / 100
    return round(peso / (altura ** 2), 1)


def classificar_imc(imc):
    if imc is None:
        return ""
    if imc < 18.5:
        return "Abaixo do peso"
    if imc < 25:
        return "Peso normal"
    if imc < 30:
        return "Sobrepeso"
    return "Obesidade"