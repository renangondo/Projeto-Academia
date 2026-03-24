from django.urls import path

from .views import EstadoCreate, CidadeCreate, AlunoCreate, ProfessorCreate
from .views import EstadoUpdate, CidadeUpdate, AlunoUpdate, ProfessorUpdate
from .views import EstadoDelete, CidadeDelete, AlunoDelete, ProfessorDelete

urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/estado/', EstadoCreate.as_view(), name="cadastrar-estado"),
    path('cadastrar/cidade/', CidadeCreate.as_view(), name = "cadastrar-cidade"),
    path('cadastrar/professor/', ProfessorCreate.as_view(), name = "cadastrar-professor"),
    path('cadastrar/aluno/', AlunoCreate.as_view(), name = "cadastrar-aluno"),

    path('editar/estado/<int:pk>/', EstadoUpdate.as_view(), name="editar-estado"),
    path('editar/cidade/<int:pk>/', CidadeUpdate.as_view(), name="editar-cidade"),
    path('editar/professor/<int:pk>/', ProfessorUpdate.as_view(), name="editar-professor"),
    path('editar/aluno/<int:pk>/', AlunoUpdate.as_view(), name="editar-aluno"),

    path('excluir/estado/<int:pk>/', EstadoDelete.as_view(), name="excluir-estado"),
    path('excluir/cidade/<int:pk>/', CidadeDelete.as_view(), name="excluir-cidade"),
    path('excluir/professor/<int:pk>/', ProfessorDelete.as_view(), name="excluir-professor"),
    path('excluir/aluno/<int:pk>/', AlunoDelete.as_view(), name="excluir-aluno"),


     

]