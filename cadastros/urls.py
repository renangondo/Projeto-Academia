from django.urls import path

from .views import PessoaDetail, PessoaList, CidadeList, EstadoCreate, CidadeCreate, PessoaCreate, EstadoList
from .views import EstadoUpdate, CidadeUpdate, PessoaUpdate
from .views import EstadoDelete, CidadeDelete, PessoaDelete

urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/estado/', EstadoCreate.as_view(), name="cadastrar-estado"),
    path('cadastrar/cidade/', CidadeCreate.as_view(), name = "cadastrar-cidade"),
    path('cadastrar/professor/', PessoaCreate.as_view(), name = "cadastrar-professor"),
    path('cadastrar/aluno/', PessoaCreate.as_view(), name = "cadastrar-aluno"),

    path('editar/estado/<int:pk>/', EstadoUpdate.as_view(), name="editar-estado"),
    path('editar/cidade/<int:pk>/', CidadeUpdate.as_view(), name="editar-cidade"),
    path('editar/professor/<int:pk>/', PessoaUpdate.as_view(), name="editar-professor"),
    path('editar/aluno/<int:pk>/', PessoaUpdate.as_view(), name="editar-aluno"),

    path('excluir/estado/<int:pk>/', EstadoDelete.as_view(), name="excluir-estado"),
    path('excluir/cidade/<int:pk>/', CidadeDelete.as_view(), name="excluir-cidade"),
    path('excluir/professor/<int:pk>/', PessoaDelete.as_view(), name="excluir-professor"),
    path('excluir/aluno/<int:pk>/', PessoaDelete.as_view(), name="excluir-aluno"),

    path('listar/estado/', EstadoList.as_view(), name="listar-estado"),
    path('listar/cidade/', CidadeList.as_view(), name="listar-cidade"),
    path('listar/professor/', PessoaList.as_view(), name="listar-professor"),
    path('listar/aluno/', PessoaList.as_view(), name="listar-aluno"),

    path('detalhe/aluno/<int:pk>/', PessoaDetail.as_view(), name='detalhe-aluno'),


]