from django.urls import path

from .views import CategoriaCreate, CategoriaDelete, CategoriaUpdate, ExercicioCreate, ExercicioDelete, ExercicioTreinoDelete, ExercicioTreinoUpdate, ExercicioUpdate, TreinoCreate, ExercicioTreinoCreate, TreinoDelete, TreinoDetail, TreinoUpdate



urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/categoria/', CategoriaCreate.as_view(), name="cadastrar-categoria"),
    path('cadastrar/treino/<int:aluno>', TreinoCreate.as_view(), name="cadastrar-treino"),
    path('cadastrar/exercicio/', ExercicioCreate.as_view(), name="cadastrar-exercicio"),
    path('treino/<int:pk>/adicionar-exercicio', ExercicioTreinoCreate.as_view(), name="cadastrar-exercicioTreino"),


    path('editar/categoria/<int:pk>', CategoriaUpdate.as_view(), name="editar-categoria"),
    path('editar/treino/<int:pk>', TreinoUpdate.as_view(), name="editar-treino"),
    path('editar/exercicio/<int:pk>', ExercicioUpdate.as_view(), name="editar-exercicio"),
    path('editar/exercicioTreino/<int:pk>', ExercicioTreinoUpdate.as_view(), name="editar-exercicioTreino"),


    path('excluir/categoria/<int:pk>', CategoriaDelete.as_view(), name="excluir-categoria"),
    path('excluir/treino/<int:pk>', TreinoDelete.as_view(), name="excluir-treino"),
    path('excluir/exercicio/<int:pk>', ExercicioDelete.as_view(), name="excluir-exercicio"),
    path('excluir/exercicioTreino/<int:pk>', ExercicioTreinoDelete.as_view(), name="excluir-exercicioTreino"),

    path('treino/<int:pk>/', TreinoDetail.as_view(), name='detalhe-treino'),




]