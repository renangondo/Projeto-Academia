from django.urls import path



urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/estado/', EstadoCreate.as_view(), name="cadastrar-estado"),
    path('cadastrar/treino', TreinoCreate.as_view(), name="cadastrar-treino"),
]