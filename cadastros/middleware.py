from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class TrocaSenhaObrigatoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            pessoa = getattr(request.user, 'pessoa_usuario', None)

            if pessoa and pessoa.precisa_trocar_senha:
                liberadas = (reverse('alterar-senha'), reverse('logout'))
                if request.path not in liberadas and not request.path.startswith(settings.STATIC_URL):
                    return redirect('alterar-senha')

        return self.get_response(request)