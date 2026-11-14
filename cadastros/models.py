from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError

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
def validar_data_nascimento(valor):
    if valor > timezone.localdate():
        raise ValidationError("A data de nascimento não pode ser no futuro.")
    if valor.year < 1900:
        raise ValidationError("Data de nascimento inválida.")
#Models Pessoa
class Pessoa(Auditoria):
    TIPO_CHOICES = [
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
        ('ADMINISTRADOR', 'Administrador')
    ]

        
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
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Pessoa")
    nome = models.CharField(max_length=50, verbose_name="Nome")
    data_nascimento = models.DateField(verbose_name="Data de nascimento",null=True,blank=True,validators=[validar_data_nascimento],)
    cpf = models.CharField(max_length=11, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=15, verbose_name="Telefone")
    objetivo = models.TextField(verbose_name="Objetivo", null=True, blank=True)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, verbose_name="Sexo", null=True, blank=True)
    nivel = models.IntegerField(choices=NIVEL_CHOICES, verbose_name="Nível", null=True, blank=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT)
    professor = models.ForeignKey("self", on_delete=models.PROTECT, related_name="alunos", limit_choices_to={"tipo": "PROFESSOR"}, null=True, blank=True)
    # Usando para referenciar o model User do próprio Django.
    usuario = models.OneToOneField("auth.User", on_delete=models.CASCADE, related_name="pessoa_usuario")
    precisa_trocar_senha = models.BooleanField(default=False, verbose_name="Precisa trocar a senha")
    
    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"

    @property
    def idade(self):
        if not self.data_nascimento:
            return None

        hoje = timezone.localdate()
        ja_fez_aniversario = (hoje.month, hoje.day) >= (
            self.data_nascimento.month, self.data_nascimento.day
        )
        return hoje.year - self.data_nascimento.year - (0 if ja_fez_aniversario else 1)
    
    @property
    def cpf_formatado(self):
        c = self.cpf or ''
        if len(c) != 11:
            return c
        return f"{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}"

    @property
    def cpf_mascarado(self):
        c = self.cpf or ''
        if len(c) != 11:
            return c
        return f"***.{c[3:6]}.{c[6:9]}-**"

    @property
    def telefone_formatado(self):
        t = ''.join(ch for ch in (self.telefone or '') if ch.isdigit())
        if len(t) == 11:
            return f"({t[:2]}) {t[2:7]}-{t[7:]}"
        if len(t) == 10:
            return f"({t[:2]}) {t[2:6]}-{t[6:]}"
        return self.telefone or ''


class TransferenciaAluno(Auditoria):
    ORIGEM_CHOICES = [
        ('PROFESSOR', 'Professor'),
        ('ALUNO', 'Aluno'),
    ]
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ACEITA', 'Aceita'),
        ('RECUSADA', 'Recusada'),
        ('EXPIRADA', 'Expirada (sem resposta)'),
    ]

    PRAZO_HORAS = 48

    aluno = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="transferencias")
    professor_atual = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="transferencias_enviadas", null=True, blank=True)
    professor_novo = models.ForeignKey(Pessoa, on_delete=models.PROTECT, related_name="transferencias_recebidas")
    origem = models.CharField(max_length=10, choices=ORIGEM_CHOICES, default='PROFESSOR')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    observacao = models.CharField(max_length=200, blank=True, null=True, verbose_name="Observação")

    def __str__(self):
        return f"{self.aluno} de {self.professor_atual} para {self.professor_novo} ({self.status})"

    @property
    def prazo_limite(self):
        return self.cadastrado_em + timedelta(hours=self.PRAZO_HORAS)

    @property
    def esta_vencida(self):
        return self.status == 'PENDENTE' and timezone.now() > self.prazo_limite

    def clean(self):
        if not self.aluno_id:
            return

        conflito = TransferenciaAluno.objects.filter(
            aluno_id=self.aluno_id,
            status='PENDENTE',
        ).exclude(pk=self.pk)

        if conflito.exists():
            raise ValidationError(
                "Já existe uma solicitação de transferência pendente para esse aluno. "
                "Aguarde a resposta ou o prazo de 48h expirar."
            )


def expirar_transferencias_vencidas():
    limite = timezone.now() - timedelta(hours=TransferenciaAluno.PRAZO_HORAS)
    TransferenciaAluno.objects.filter(
        status='PENDENTE',
        cadastrado_em__lt=limite,
    ).update(status='EXPIRADA')

