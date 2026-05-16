from django.urls import path

from .views import CategoriaCreate, ExercicioCreate, TreinoCreate, ExercicioTreinoCreate



urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),
    path('cadastrar/treino/', TreinoCreate.as_view(), name="cadastrar-treino"),
    path('cadastrar/exercicio/', ExercicioCreate.as_view(), name="cadastrar-exercicio"),
    path('cadastrar/exercicioTreino/', ExercicioTreinoCreate.as_view(), name="cadatrar-exercicioTreino")
]