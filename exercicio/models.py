from django.db import models

from cadastros.models import Auditoria, Pessoa

# Create your models here.

class Categoria(Auditoria):
    nome = models.CharField(max_length=100, verbose_name="Categoria")

    def __str__(self):
        return "Categoria do treino: {}".format(self.nome)

###########################################################################################
class Treino(Auditoria):
    aluno = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="Treinos")
    nome_treino = models.CharField(max_length=20, verbose_name="Nome do Treino")
    data_inicio = models.DateField(verbose_name="Data de Inicio")
    data_fim = models.DateField(verbose_name="Data de Encerramento")
    descricao = models.CharField(max_length=100, verbose_name="Descrição")
    cadastrado_por = models.ForeignKey(Pessoa, on_delete=models.PROTECT)

    def __str__(self):
        return "{} Treino: {}".format(self.aluno, self.nome_treino)


###########################################################################################

class Exercicio(Auditoria):
    nome = models.CharField(max_length=100, verbose_name="Nome do Exercicio")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=150, verbose_name="Descrição")
    cadastrado_por = models.ForeignKey(Pessoa, on_delete=models.PROTECT)

    def __str__(self):
        return "{} ({})".format(self.nome, self.categoria)

###########################################################################################

class ExercicioTreino(Auditoria):
    treino = models.ForeignKey(Treino, on_delete=models.PROTECT, related_name="exercicio_do_treino")
    exercicio = models.ForeignKey(Exercicio, on_delete=models.PROTECT)
    series = models.IntegerField(verbose_name="Séries")
    repeticoes = models.IntegerField(verbose_name="Repetições")
    descanso = models.IntegerField(verbose_name="Descanso")
    peso_atual = models.FloatField(verbose_name="Peso Atual")
    cadastrado_por = models.ForeignKey(Pessoa, on_delete=models.PROTECT)

    def __str__(self):
        return "({}) {} {} Séries {} Rep".format(self.treino, self.exercicio, self.series, self.repeticoes)


