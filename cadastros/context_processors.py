def usuario_grupos(request):

    if request.user.is_authenticated:

        return {
            "is_admin":
                request.user.groups.filter(
                    name="Administrador"
                ).exists(),

            "is_professor":
                request.user.groups.filter(
                    name="Professor"
                ).exists(),

            "is_aluno":
                request.user.groups.filter(
                    name="Aluno"
                ).exists(),
        }

    return {}