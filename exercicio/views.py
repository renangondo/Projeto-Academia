from django.views.generic.edit import CreateView
from .models import Categoria, Treino, Exercicio, ExercicioTreino
from django.urls import reverse_lazy


# Create your views here.

class CategoriaCreate(CreateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')


class TreinoCreate(CreateView):
    model = Treino
    fields = ['aluno', 'nomeTreino', 'dataInicio', 'dataFim', 'descricao', 'cadastradoEm', 'cadastradoPor']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')


class ExercicioCreate(CreateView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')

class ExercicioTreinoCreate(CreateView):
    model = ExercicioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'cadastraoEm', 'pesoAtual']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
