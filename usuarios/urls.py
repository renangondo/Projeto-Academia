from django.urls import path
from django.contrib.auth import views as auth_views

from usuarios.views import AlterarSenhaView


urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('', auth_views.LoginView.as_view(
        template_name = 'usuarios/login.html'
    ), name="login"),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path('alterar-senha/', AlterarSenhaView.as_view(), name='alterar-senha'),

      
]