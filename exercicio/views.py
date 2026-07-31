from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User

from cadastros.models import Pessoa
from .models import Categoria, Treino, Exercicio, ExercicioTreino
from django.views.generic import DetailView
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin


# Create your views here.

class CategoriaCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]


class TreinoCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Treino
    fields = ['aluno', 'nome_treino', 'data_inicio', 'data_fim', 'descricao']
    template_name = 'form.html'
    group_required = ["Professor", "Administrador"]

    def get_initial(self):
        initial = super().get_initial()
        if 'aluno' in self.kwargs:
            try:
                aluno = Pessoa.objects.get(pk=self.kwargs['aluno'])
                initial['aluno'] = aluno
            except Pessoa.DoesNotExist:
                initial['aluno'] = None
                        
        return initial
    
    def form_valid(self, form):
        form.instance.cadastrado_por = self.request.user.pessoa_usuario
        return super().form_valid(form)
    
    def get_success_url(self):

        return reverse_lazy('detalhe-aluno', kwargs={'pk': self.object.aluno.pk})
    


class ExercicioCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]

    def form_valid(self, form):
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)

class ExercicioTreinoCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = ExercicioTreino
    fields = ['exercicio', 'series', 'repeticoes', 'descanso', 'peso_atual']
    template_name = 'form_exercicio_treino.html'
    group_required = ["Professor", "Administrador"]

    def form_valid(self, form):
        treino = Treino.objects.get(pk=self.kwargs['pk'])
        form.instance.treino = treino
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detalhe-treino', kwargs={'pk': self.kwargs['pk']})

############################## UPDATE #########################################


class CategoriaUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]


class TreinoUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Treino
    fields = ['aluno', 'nome_treino', 'data_inicio', 'data_fim', 'descricao']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]

class ExercicioUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]

class ExercicioTreinoUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = ExercicioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'peso_atual']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]
############################## DELETE #########################################

class CategoriaDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Categoria
    fields = ['nome']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]


class TreinoDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Treino
    fields = ['aluno', 'nome_treino', 'data_inicio', 'data_fim', 'descricao']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]



class ExercicioDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]

class ExercicioTreinoDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = ExercicioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'peso_atual']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]


############################## DETAIL #########################################

class TreinoDetail(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Treino
    template_name = 'detalhe_treino.html'
    context_object_name = 'treino'
    group_required = ["Professor", "Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['exercicios_treino'] = ExercicioTreino.objects.filter(
            treino=self.object
        ).select_related('exercicio', 'exercicio__categoria')

        return context
    

