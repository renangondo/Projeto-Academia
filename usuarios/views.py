from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

# Create your views here.
from django.contrib.auth import logout
from django.shortcuts import redirect


def LogoutView(request):
    logout(request)
    return redirect('login')


class AlterarSenhaView(PasswordChangeView):
    template_name = 'usuarios/alterar_senha.html'
    success_url = reverse_lazy('meu-perfil')

    def form_valid(self, form):
        messages.success(self.request, "Senha alterada com sucesso.")
        return super().form_valid(form)