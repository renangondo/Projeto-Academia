from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import DetailView

from exercicio.models import Treino
from .models import Cidade, Estado, Professor, Aluno
from django.urls import reverse_lazy

# Create your views here.

####CREATE VIEW#####
class EstadoCreate(CreateView):
    model = Estado  # Qual modelo que será cadastrado
    fields = ['nome', 'sigla'] # Quais campos que irá aparecer para cadastrar
    template_name = 'cadastros/form.html' # Qual template será usado
    success_url = reverse_lazy('inicio') # Onde será redirecionado


class CidadeCreate(CreateView):
    model = Cidade
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class ProfessorCreate(CreateView):
    model = Professor
    fields = ['nome', 'cpf', 'telefone', 'cidade']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class AlunoCreate(CreateView):
    model = Aluno
    fields = ['nome', 'idade', 'cpf', 'telefone', 'objetivo', 'data_criacao', 'sexo', 'nivel', 'cidade', 'professor']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


############################## UPDATE #########################################

class EstadoUpdate(UpdateView):
    model = Estado
    fields= ['nome', 'sigla']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')

class CidadeUpdate(UpdateView):
    model = Cidade
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class ProfessorUpdate(UpdateView):
    model = Professor
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class AlunoUpdate(UpdateView):
    model = Aluno
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


############################## DELETE #########################################

class EstadoDelete(DeleteView):
    model = Estado
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


class CidadeDelete(DeleteView):
    model = Cidade
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


class ProfessorDelete(DeleteView):
    model = Professor
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


class AlunoDelete(DeleteView):
    model = Aluno
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


############################## LISTAR #########################################

class EstadoList(ListView):
    model = Estado
    template_name = 'cadastros/listar_estado.html'


class CidadeList(ListView):
    model = Cidade
    template_name = 'cadastros/listar_cidades.html'


class ProfessorList(ListView):
    model = Professor
    template_name = 'cadastros/listar_professores.html'


class AlunoList(ListView):
    model = Aluno
    template_name = 'cadastros/listar_alunos.html'


############################## DETAIL #########################################

class AlunoDetail(DetailView):
    model = Aluno
    template_name = 'cadastros/detalhe_aluno.html'
    context_object_name = 'aluno'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['treinos'] = Treino.objects.filter(
            aluno=self.object
        ).order_by('-dataInicio')

        return context