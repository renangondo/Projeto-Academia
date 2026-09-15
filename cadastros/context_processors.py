from cadastros.models import TransferenciaAluno


def usuario_grupos(request):

    contexto = {
        "is_admin": False,
        "is_professor": False,
        "is_aluno": False,
        "qtd_transferencias_pendentes": 0,
    }

    if request.user.is_authenticated:

        contexto["is_admin"] = (
            request.user.is_superuser or
            request.user.groups.filter(name="Administrador").exists()
        )

        contexto["is_professor"] = request.user.groups.filter(
            name="Professor"
        ).exists()

        contexto["is_aluno"] = request.user.groups.filter(
            name="Aluno"
        ).exists()

        if contexto["is_professor"]:
            pessoa = getattr(request.user, "pessoa_usuario", None)

            if pessoa:
                contexto["qtd_transferencias_pendentes"] = TransferenciaAluno.objects.filter(
                    professor_novo=pessoa, status="PENDENTE"
                ).count()

    return contexto