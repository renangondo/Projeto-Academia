from django.urls import path
from .views import InicioView

urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'), 
    path('', InicioView.as_view(), name='inicio'),  
]