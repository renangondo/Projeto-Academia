from django.urls import path

from medidas.views import MedidasCreate, MedidasDelete, MedidasUpdate


urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/medidas/', MedidasCreate.as_view(), name="cadastrar-medidas"),

    path('editar/medidas/<int:pk>', MedidasUpdate.as_view(), name="editar-medidas"),

    path('excluir/medidas/<int:pk>', MedidasDelete.as_view(), name="excluir-medidas"),



]