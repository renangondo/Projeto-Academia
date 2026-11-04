from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User

from cadastros.models import Pessoa
from .models import Categoria, Treino, Exercicio, ExercicioTreino
from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from django.db.models import Count, ProtectedError
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404


from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin


# Create your views here.

from django.db.models import Q

def exercicios_visiveis(user):
    if user.is_superuser or user.groups.filter(name="Administrador").exists():
        return Exercicio.objects.all()

    pessoa = user.pessoa_usuario
    return Exercicio.objects.filter(
        Q(cadastrado_por=pessoa)
        | Q(cadastrado_por__usuario__is_superuser=True)
        | Q(cadastrado_por__usuario__groups__name="Administrador")
    ).distinct()

############################## A MAIS #########################################
class SomenteMeusTreinosMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Administrador").exists():
            return qs
        return qs.filter(aluno__professor=user.pessoa_usuario)
    
class SomenteMeusExerciciosMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Administrador").exists():
            return qs
        return qs.filter(cadastrado_por=user.pessoa_usuario)

    
############################## CREATE #########################################
class CategoriaCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('listar-categoria')
    group_required = ["Administrador"]


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
    group_required = ["Professor", "Administrador"]

    def get_initial(self):
        initial = super().get_initial()
        categoria = self.request.GET.get('categoria')
        if categoria:
            initial['categoria'] = categoria   # já vem selecionada ao clicar em "Novo exercício"
        return initial

    def form_valid(self, form):
        form.instance.cadastrado_por = self.request.user.pessoa_usuario
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('listar-exercicio-categoria', kwargs={'pk': self.object.categoria_id})



class ExerciciosPorCategoriaMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exercicios = exercicios_visiveis(self.request.user)

        context['categorias_json'] = [
            {"id": c.pk, "nome": c.nome}
            for c in Categoria.objects.order_by('nome')
        ]
        context['exercicios_json'] = [
            {"id": e.pk, "nome": e.nome, "categoria": e.categoria_id}
            for e in exercicios
        ]
        return context

class ExercicioTreinoCreate(ExerciciosPorCategoriaMixin, LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = ExercicioTreino
    fields = ['exercicio', 'series', 'repeticoes', 'descanso', 'peso_atual']
    template_name = 'form_exercicio_treino.html'
    group_required = ["Professor", "Administrador"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['exercicio'].queryset = exercicios_visiveis(self.request.user)
        return form

    def form_valid(self, form):
        treino = Treino.objects.get(pk=self.kwargs['pk'])
        form.instance.treino = treino
        form.instance.cadastrado_por = self.request.user.pessoa_usuario  # lembrando: já corrigimos isso antes
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detalhe-treino', kwargs={'pk': self.kwargs['pk']})

############################## UPDATE #########################################


class CategoriaUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('listar-categoria')
    group_required = ["Administrador"]


class TreinoUpdate(SomenteMeusTreinosMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Treino
    fields = ['nome_treino', 'data_inicio', 'data_fim', 'descricao']
    template_name = 'form.html'
    group_required = ["Professor", "Administrador"]

    def get_success_url(self):
        return reverse_lazy('detalhe-treino', kwargs={'pk': self.object.pk})

class ExercicioUpdate(SomenteMeusExerciciosMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Exercicio
    fields = ['nome', 'categoria', 'descricao']
    template_name = 'form.html'
    group_required = ["Professor", "Administrador"]

    def get_success_url(self):
        return reverse_lazy('listar-exercicio-categoria', kwargs={'pk': self.object.categoria_id})

class ExercicioTreinoUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = ExercicioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'peso_atual']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['exercicio'].queryset = exercicios_visiveis(self.request.user)
        return form
############################## DELETE #########################################

class CategoriaDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Categoria
    fields = ['nome']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Administrador"]

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Não é possível excluir: existem exercícios cadastrados nessa categoria."
            )
            return HttpResponseRedirect(self.get_success_url())


class TreinoDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Treino
    fields = ['aluno', 'nome_treino', 'data_inicio', 'data_fim', 'descricao']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('listar-categoria')
    group_required = ["Professor", "Administrador"]



class ExercicioDelete(SomenteMeusExerciciosMixin, LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Exercicio
    template_name = 'form-excluir.html'
    group_required = ["Professor", "Administrador"]

    def get_success_url(self):
        return reverse_lazy('listar-exercicio-categoria', kwargs={'pk': self.object.categoria_id})

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Não é possível excluir: esse exercício já está sendo usado em treinos."
            )
            return HttpResponseRedirect(self.get_success_url())

class ExercicioTreinoDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = ExercicioTreino
    fields = ['treino', 'exercicio', 'series', 'repeticoes', 'descanso', 'peso_atual']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Professor", "Administrador"]


############################## DETAIL #########################################

class TreinoDetail(SomenteMeusTreinosMixin, LoginRequiredMixin, GroupRequiredMixin, DetailView):
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

############################## LIST #########################################

class ExercicioList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Exercicio
    template_name = "exercicio/listar_exercicio.html"
    group_required = ["Professor", "Administrador"]

    def get_queryset(self):
        return exercicios_visiveis(self.request.user)


class CategoriaList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Categoria
    template_name = 'listar_categoria.html'
    context_object_name = 'categorias'
    group_required = ["Administrador"]

    def get_queryset(self):
        return Categoria.objects.annotate(
            qtd_exercicios=Count('exercicio')
        ).order_by('nome')


class ExercicioPorCategoriaList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Exercicio
    template_name = 'listar_exercicio_categoria.html'
    context_object_name = 'exercicios'
    group_required = ["Professor", "Administrador"]

    def get_queryset(self):
        self.categoria = get_object_or_404(Categoria, pk=self.kwargs['pk'])
        return exercicios_visiveis(self.request.user).filter(
            categoria=self.categoria
        ).select_related('cadastrado_por__usuario').order_by('nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoria'] = self.categoria
        return context

