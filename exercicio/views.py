from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Categoria, Treino, Exercicio, ExericioTreino
from django.urls import reverse_lazy


# Create your views here.

class CategoriaCreate(CreateView):
    model = Categoria
    fields = ['nome']
    template_name = 'exercicio/form.html'
    success_url = reverse_lazy('inicio')


class TreinoCreate(CreateView):
    model = Treino
    fields = ['aluno', 'nomeTreino', 'dataInicio', 'dataFim', 'descricao', 'cadastradoEm', 'cadastradoPor']
    template_name = 'exercicio/form.hmtl'
    success_url = reverse_lazy('inicio')


class ExercicioCreate(CreateView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = ('exericico/form.html')
    success_url = reverse_lazy('inicio')

class ExercicioTreinoCreate(CreateView):
    model = ExericioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'cadastradoEm', 'PesoAtual']
    template_name = ('exericico/form.html')
    success_url = reverse_lazy('inicio')
