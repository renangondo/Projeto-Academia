from django.db import models

from cadastros.models import Aluno, Professor

# Create your models here.

class Treino(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.PROTECT)
    nomeTreino = models.CharField(max_length=20, verbose_name="Nome do Treino")
    dataInicio = models.DateField(verbose_name="Data de Inicio")
    dataFim = models.DateField(verbose_name="Data de Encerramento")
    descricao = models.CharField(max_length=100, verbose_name="Descrição")
    cadastradoEm = models.DateTimeField(verbose_name="Cadastrado em")
    cadastradoPor = models.ForeignKey(Professor, on_delete=models.PROTECT)

    def __str__(self):
        return "{} Treino: {}".format(self.aluno, self.nomeTreino)

###########################################################################################

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Categoria")

    def __str__(self):
        return "Categoria do treino: {}".format(self.nome)

###########################################################################################

class Exercicio(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Exercicio")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=150, verbose_name="Descrição")

    def __str__(self):
        return "{} ({})".format(self.nome, self.categoria)

###########################################################################################

class ExericioTreino(models.Model):
    treino = models.ForeignKey(Treino, on_delete=models.PROTECT)
    exercicio = models.ForeignKey(Exercicio, on_delete=models.PROTECT)
    series = models.IntegerField(verbose_name="Séries")
    repeticoes = models.IntegerField(verbose_name="Repetições")
    descanso = models.IntegerField(verbose_name="Descanso")
    cadastraoEm = models.DateField(verbose_name="Cadastrado em")
    pesoAtual = models.FloatField(verbose_name="Peso Atual")


