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