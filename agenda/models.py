from django.db import models

# Create your models here.

# agenda/models.py
from django.db import models
from django.core.exceptions import ValidationError

from cadastros.models import Auditoria, Pessoa


class HorarioAula(Auditoria):
    DIA_CHOICES = [
        (1, 'Segunda-feira'),
        (2, 'Terça-feira'),
        (3, 'Quarta-feira'),
        (4, 'Quinta-feira'),
        (5, 'Sexta-feira'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]

    aluno = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="horarios_aluno", limit_choices_to={"tipo": "ALUNO"})
    professor = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="horarios_professor", limit_choices_to={"tipo": "PROFESSOR"})
    dia_semana = models.IntegerField(choices=DIA_CHOICES, verbose_name="Dia da semana")
    horario = models.TimeField(verbose_name="Horário")

    class Meta:
        ordering = ["dia_semana", "horario"]
        unique_together = ("professor", "dia_semana", "horario")  # trava no banco também

    def clean(self):
        conflito = HorarioAula.objects.filter(
            professor=self.professor,
            dia_semana=self.dia_semana,
            horario=self.horario,
        ).exclude(pk=self.pk)

        if conflito.exists():
            raise ValidationError(
                "Você já tem uma aula marcada nesse dia e horário. Escolha outro horário."
            )

    def __str__(self):
        return f"{self.aluno.nome} - {self.get_dia_semana_display()} às {self.horario}"