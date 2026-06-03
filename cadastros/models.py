from django.db import models

# Classe de auditoria usada para todos
class Auditoria(models.Model):
    cadastrado_em = models.DateTimeField(auto_now_add=True, verbose_name="Cadastrado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        abstract = True
    
# Models Estado
class Estado(Auditoria):
    nome = models.CharField(max_length=50, verbose_name="Nome do Estado")
    sigla = models.CharField(max_length=2, verbose_name="Sigla")

    def __str__(self):
        return "{} ({})".format(self.nome, self.sigla)
    
###########################################################################################

# Models Cidade
class Cidade(Auditoria):
    nome = models.CharField(max_length=50, verbose_name="Nome da Cidade")
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)

    def __str__(self):
        return "{} ({})".format(self.nome, self.estado.sigla)

###########################################################################################
#Models Pessoa
class Pessoa(Auditoria):
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
    
    nome = models.CharField(max_length=50, verbose_name="Nome")
    idade = models.IntegerField(verbose_name="Idade", null=True, blank=True)
    cpf = models.CharField(max_length=11, verbose_name="CPF")
    telefone = models.CharField(max_length=15, verbose_name="Telefone")
    objetivo = models.CharField(max_length=255, verbose_name="Objetivo", null=True, blank=True)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, verbose_name="Sexo", null=True, blank=True)
    nivel = models.IntegerField(choices=NIVEL_CHOICES, verbose_name="Nível", null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    professor = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="alunos_professor", null=True, blank=True)
    
    # Usando para referenciar o model User do próprio Django.
    usuario = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="pessoa_usuario")
    
    def __str__(self):
        return self.nome





