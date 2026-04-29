from django.urls import path

from .views import EstadoCreate, CidadeCreate, AlunoCreate, ProfessorCreate
from .views import EstadoUpdate, CidadeUpdate, AlunoUpdate, ProfessorUpdate
from .views import EstadoDelete, CidadeDelete, AlunoDelete, ProfessorDelete

urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/estado/', EstadoCreate.as_view(), name="cadastrar-estado"),
]