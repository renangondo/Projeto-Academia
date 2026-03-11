from django.urls import path
from .views import PaginaModelo

urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'), 
    path('inicio/', PaginaModelo.as_view(), name='inicio'),  
]