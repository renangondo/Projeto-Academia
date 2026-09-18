# agenda/urls.py
from django.urls import path
from .views import HorarioAulaCreate, AgendaProfessorList, AgendaAlunoList, HorarioAulaDelete

urlpatterns = [
    path('agendar/', HorarioAulaCreate.as_view(), name="agendar-aula"),
    path('minha-agenda/', AgendaProfessorList.as_view(), name="minha-agenda"),
    path('minha-agenda/aluno/', AgendaAlunoList.as_view(), name="minha-agenda-aluno"),
    path('excluir/<int:pk>/', HorarioAulaDelete.as_view(), name="excluir-horario"),
]