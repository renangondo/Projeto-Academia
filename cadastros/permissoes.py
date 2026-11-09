from .models import Pessoa


def eh_admin(user):
    return user.is_superuser or user.groups.filter(name="Administrador").exists()


def eh_professor(user):
    return user.groups.filter(name="Professor").exists()


def eh_aluno(user):
    return user.groups.filter(name="Aluno").exists()


def alunos_do_usuario(user):
    """Alunos que esse usuário pode acessar:
    admin = todos | professor = só os dele | aluno = só ele mesmo."""
    if eh_admin(user):
        return Pessoa.objects.filter(tipo="ALUNO")

    pessoa = getattr(user, "pessoa_usuario", None)
    if pessoa is None:
        return Pessoa.objects.none()

    if eh_professor(user):
        return Pessoa.objects.filter(tipo="ALUNO", professor=pessoa)
    if eh_aluno(user):
        return Pessoa.objects.filter(pk=pessoa.pk)
    return Pessoa.objects.none()


class SomenteDoMeuAlunoMixin:
    """Filtra o queryset da view pelos alunos que o usuário pode acessar.
    `campo_aluno` diz qual campo do model liga ao aluno."""
    campo_aluno = "aluno"

    def get_queryset(self):
        return super().get_queryset().filter(
            **{f"{self.campo_aluno}__in": alunos_do_usuario(self.request.user)}
        )


class SomenteMeuPerfilProfessorMixin:
    """Professor só mexe no próprio perfil; admin mexe em qualquer um."""
    def get_queryset(self):
        qs = super().get_queryset().filter(tipo="PROFESSOR")
        if eh_admin(self.request.user):
            return qs
        return qs.filter(pk=self.request.user.pessoa_usuario.pk)