from django.utils import timezone

from .models import HistoricoCarga


def registrar_carga(aluno, exercicio, carga, usuario):
    """Um registro por exercício por dia: se já existe o de hoje, atualiza."""
    registro, criado = HistoricoCarga.objects.get_or_create(
        aluno=aluno,
        exercicio=exercicio,
        data=timezone.localdate(),
        defaults={'carga': carga, 'registrado_por': usuario},
    )

    if not criado and registro.carga != carga:
        registro.carga = carga
        registro.registrado_por = usuario
        registro.save()

    return registro