from django.urls import path

from .views import EstadoCreate, CidadeCreate, AlunoCreate, ProfessorCreate

urlpatterns = [
    # path('Endereço/', MinhaView.as_view(), name='nome-da-url'),
    path('cadastrar/estado/', EstadoCreate.as_view(), name="cadastrar-estado"),
    path('cadastrar/cidade/', CidadeCreate.as_view(), name = "cadastrar-cidade"),
    path('cadastrar/professor/', ProfessorCreate.as_view(), name = "cadastrar-professor"),
    path('cadastrar/aluno/', AlunoCreate.as_view(), name = "cadastrar-aluno"),

     

]