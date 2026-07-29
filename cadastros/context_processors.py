def usuario_grupos(request):

    contexto = {
        "is_admin": False,
        "is_professor": False,
        "is_aluno": False,
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

    return contexto