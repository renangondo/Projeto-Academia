from django.views.generic.edit import CreateView, UpdateView, DeleteView

from cadastros.models import Aluno
from .models import Categoria, Treino, Exercicio, ExercicioTreino
from django.views.generic import DetailView
from django.urls import reverse_lazy


# Create your views here.

class CategoriaCreate(CreateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')


class TreinoCreate(CreateView):
    model = Treino
    fields = ['nomeTreino', 'dataInicio', 'dataFim', 'descricao', 'cadastradoPor']
    template_name = 'form.html'
    
    def form_valid(self, form):
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])
        form.instance.aluno = aluno
        return super().form_valid(form)
    def get_success_url(self):

        return reverse_lazy('detalhe-aluno', kwargs={'pk': self.kwargs['pk']})
    success_url = reverse_lazy('inicio')


class ExercicioCreate(CreateView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')

class ExercicioTreinoCreate(CreateView):
    model = ExercicioTreino
    fields = ['exercicio', 'series', 'repeticoes', 'descanso', 'pesoAtual']
    template_name = 'form_exercicio_treino.html'

    def form_valid(self, form):
        treino = Treino.objects.get(pk=self.kwargs['pk'])
        form.instance.treino = treino
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detalhe-treino', kwargs={'pk': self.kwargs['pk']})

############################## UPDATE #########################################


class CategoriaUpdate(UpdateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')


class TreinoUpdate(UpdateView):
    model = Treino
    fields = ['aluno', 'nomeTreino', 'dataInicio', 'dataFim', 'descricao', 'cadastradoPor']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')


class ExercicioUpdate(UpdateView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')

class ExercicioTreinoUpdate(UpdateView):
    model = ExercicioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'pesoAtual']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')

############################## DELETE #########################################

class CategoriaDelete(DeleteView):
    model = Categoria
    fields = ['nome']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')


class TreinoDelete(DeleteView):
    model = Treino
    fields = ['aluno', 'nomeTreino', 'dataInicio', 'dataFim', 'descricao', 'cadastradoPor']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')


class ExercicioDelete(DeleteView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')

class ExercicioTreinoDelete(DeleteView):
    model = ExercicioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'pesoAtual']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')


############################## DETAIL #########################################

class TreinoDetail(DetailView):
    model = Treino
    template_name = 'detalhe_treino.html'
    context_object_name = 'treino'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['exercicios_treino'] = ExercicioTreino.objects.filter(
            treino=self.object
        ).select_related('exercicio', 'exercicio__categoria')

        return context
    

