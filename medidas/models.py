from django.db import models

from cadastros.models import Auditoria

# Create your models here.

class Medidas(Auditoria):
    aluno = models.ForeignKey("auth.User", on_delete=models.PROTECT)
    altura = models.FloatField(verbose_name="Altura")
    peso = models.FloatField(verbose_name="Peso")
    cintura = models.FloatField(verbose_name="Cintura")
    quadril = models.FloatField(verbose_name="Quadril")
    braco_direito = models.FloatField(verbose_name="Braço Direito")
    braco_esquerdo = models.FloatField(verbose_name="Braço Esquerdo")
    coxa_direita = models.FloatField(verbose_name="Coxa Direita")
    coxa_esquerda = models.FloatField(verbose_name="Coxa Esquerda")
    panturrilha_direita = models.FloatField(verbose_name="Panturrilha Direita")
    panturrilha_esquerda = models.FloatField(verbose_name="Panturrilha Esquerda")
    peito = models.FloatField(verbose_name="Peito")
    data_medida = models.DateField(verbose_name="Data da medida")
    cadastrado_por = models.ForeignKey("auth.User", on_delete=models.PROTECT)

    def __str__(self):
        return "{} {} {} {} {} {} {} {} {} {} {} {} ({})".format(self.aluno, self.altura, self.peso, self.cintura, self.quadril, self.braco_direito, self.braco_esquerdo, self.coxa_direita, self.coxa_esquerda, self.panturrilha_direita, self.panturrilha_esquerda, self.peito, self.data_medida)