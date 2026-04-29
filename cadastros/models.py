from django.db import models

# Models Estado
class Estado(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome do Estado")
    sigla = models.CharField(max_length=2, verbose_name="Sigla")

    def __str__(self):
        return "{} ({})".format(self.nome, self.sigla)
    
###########################################################################################

# Models Cidade
class Cidade(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome da Cidade")
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    def __str__(self):
        return "{} ({})".format(self.nome, self.estado.sigla)

###########################################################################################
#Models Professor
class Professor(models.Model):
    nome = models.CharField(max_length=50, verbose_name="Nome do Professor")
    cpf = models.CharField(max_length=11, verbose_name="CPF")
    telefone = models.CharField(max_length=15, verbose_name="Telefone")
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)

    def __str__(self):
        return "{} ({})".format(self.nome, self.cidade.nome)

###########################################################################################
#Models Aluno
class Aluno(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    NIVEL_CHOICES = [
        (1, 'Iniciante'),
        (2, 'Intermediário'), 
        (3, 'Avançado'),
    ]
    
    nome = models.CharField(max_length=50, verbose_name="Nome do Aluno")
    idade = models.IntegerField(verbose_name="Idade")
    cpf = models.CharField(max_length=11, verbose_name="CPF")
    telefone = models.CharField(max_length=15, verbose_name="Telefone")
    objetivo = models.CharField(max_length=255, verbose_name="Objetivo do Aluno")
    data_criacao = models.DateField(verbose_name="Data de criação")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, verbose_name="Sexo")
    nivel = models.CharField(max_length=1, choices=NIVEL_CHOICES, verbose_name="Nivel do Aluno")
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    professor = models.ForeignKey(Professor, on_delete=models.PROTECT)

    
    # Método que define como o objeto será exibido como string
    # Retorna: "Nome do Aluno (Idade anos)" - Ex: "João Silva (25 anos)"
    def __str__(self):
        return "{} ({} anos)".format(self.nome, self.idade)





