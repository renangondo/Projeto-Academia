from django.db import models

from cadastros.models import Aluno

# Create your models here.

class Medidas(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT)
    altura = models.FloatField(verbose_name="Altura")
    peso = models.FloatField(verbose_name="Peso")
    cintura = models.FloatField(verbose_name="Cintura")
    quadril = models.FloatField(verbose_name="Quadril")
    bracoDireito = models.FloatField(verbose_name="Braço Direito")
    bracoEsquerdo = models.FloatField(verbose_name="Braço Esquerdo")
    coxaDireita = models.FloatField(verbose_name="Coxa Direita")
    coxaEsquerda = models.FloatField(verbose_name="Coxa Esquerda")
    panturrilhaDireita = models.FloatField(verbose_name="Panturrilha Direita")
    panturrilhaEsquerda = models.FloatField(verbose_name="Panturrilha Esquerda")
    peito = models.FloatField(verbose_name="Peito")
    dataMedida = models.DateField(verbose_name="Data da medida")

    def __str__(self):
        return "{} {} {} {} {} {} {} {} {} {} {} {} ({})".format(self.aluno, self.altura, self.peso, self.cintura, self.quadril, self.bracoDireito, self.bracoEsquerdo, self.coxaDireita, self.coxaEsquerda, self.panturrilhaDireita, self.panturrilhaEsquerda, self.peito, self.dataMedida)