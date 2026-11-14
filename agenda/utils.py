from datetime import timedelta
from django.utils import timezone
from datetime import datetime, timedelta
from .models import HorarioAula

ABREVIACOES = {1: "Seg", 2: "Ter", 3: "Qua", 4: "Qui", 5: "Sex", 6: "Sáb", 7: "Dom"}


def montar_semana(horarios):
    """Agrupa as aulas por dia da semana e marca qual dia é hoje."""
    hoje = timezone.localdate()
    segunda = hoje - timedelta(days=hoje.isoweekday() - 1)

    por_dia = {numero: [] for numero, _ in HorarioAula.DIA_CHOICES}
    for horario in horarios:
        por_dia[horario.dia_semana].append(horario)

    semana = []
    for numero, nome in HorarioAula.DIA_CHOICES:
        data = segunda + timedelta(days=numero - 1)
        semana.append({
            "numero": numero,
            "nome": nome,
            "abreviado": ABREVIACOES[numero],
            "data": data,
            "eh_hoje": data == hoje,
            "horarios": por_dia[numero],
        })
    return semana


def proxima_aula(horarios):
    """Próxima aula a partir de agora (as aulas se repetem toda semana)."""
    agora = timezone.localtime()
    proxima = None

    for h in horarios:
        dias = (h.dia_semana - agora.isoweekday()) % 7
        momento = timezone.make_aware(
            datetime.combine(agora.date() + timedelta(days=dias), h.horario)
        )
        if momento < agora:
            momento += timedelta(days=7)

        if proxima is None or momento < proxima['momento']:
            proxima = {'horario': h, 'momento': momento}

    if proxima:
        diferenca = (proxima['momento'].date() - agora.date()).days
        if diferenca == 0:
            proxima['quando'] = 'Hoje'
        elif diferenca == 1:
            proxima['quando'] = 'Amanhã'
        else:
            proxima['quando'] = proxima['horario'].get_dia_semana_display()

    return proxima