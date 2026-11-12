from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse

# Create your views here.
from django.contrib.auth import logout
from django.shortcuts import redirect


def LogoutView(request):
    logout(request)
    return redirect('login')


class AlterarSenhaView(PasswordChangeView):
    template_name = 'usuarios/alterar_senha.html'

    def form_valid(self, form):
        pessoa = getattr(self.request.user, 'pessoa_usuario', None)
        self.primeiro_acesso = bool(pessoa and pessoa.precisa_trocar_senha)

        response = super().form_valid(form)

        if self.primeiro_acesso:
            pessoa.precisa_trocar_senha = False
            pessoa.save(update_fields=['precisa_trocar_senha'])

        messages.success(self.request, "Senha alterada com sucesso.")
        return response

    def get_success_url(self):
        return reverse('inicio' if getattr(self, 'primeiro_acesso', False) else 'meu-perfil')