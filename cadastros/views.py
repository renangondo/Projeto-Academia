from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import DetailView

from exercicio.models import Treino
from medidas.models import Medidas
from django.contrib.auth.models import User
from .models import Cidade, Estado, Professor, Aluno
from django.urls import reverse_lazy

# Importar o mixin de login e grupo
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin

# Create your views here.

####CREATE VIEW#####
class EstadoCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Estado  # Qual modelo que será cadastrado
    fields = ['nome', 'sigla'] # Quais campos que irá aparecer para cadastrar
    template_name = 'cadastros/form.html' # Qual template será usado
    success_url = reverse_lazy('inicio') # Onde será redirecionado
    group_required = ["Administrador"]


class CidadeCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Cidade
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Administrador"]


class ProfessorCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Professor
    fields = ['nome', 'cpf', 'telefone', 'cidade']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Administrador"]


class AlunoCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Aluno
    fields = ['nome', 'idade', 'cpf', 'telefone', 'objetivo', 'sexo', 'nivel', 'cidade', 'professor']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')
    group_required = ["Administrador", "Professor"]

    # Ao cadastrar o aluno, cria um usuário para ele
    def form_valid(self, form):
        
        try:
            usuario = User.objects.create_user(
                username=form.cleaned_data['cpf'],
                password=form.cleaned_data['cpf']
            )
            form.instance.usuario = usuario
            form.instance.professor = self.request.user
            # Tenta criar o objeto no banco de dados
            url = super().form_valid(form)
        except Exception as e:
            #Adiciona um erro no formulário
            form.add_error(None, "Houve um problema na criação do usuário, tente novamente.")
            usuario.delete()
            # Retorna None para que o form seja renderizado novamente
            return None
        
        return url
        

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
    fields = ['nome', 'idade', 'cpf', 'telefone', 'objetivo', 'sexo', 'nivel', 'cidade', 'professor']
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
    fields = ['nome', 'cpf', 'telefone', 'cidade']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class AlunoUpdate(UpdateView):
    model = Aluno
    fields = ['nome', 'idade', 'cpf', 'telefone', 'objetivo', 'sexo', 'nivel', 'cidade', 'professor']
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

    # Sobrescrever o método get_queryset para personalizar a consulta
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Se o usuário for do grupo "Administrador", liste tudo
        if self.request.user.groups.filter(name='Administrador').exists():
            return queryset
        # Se não, liste apenas os alunos do professor
        else:
            return queryset.filter(professor=self.request.user)


############################## DETAIL #########################################

class AlunoDetail(DetailView):
    model = Aluno
    template_name = 'cadastros/detalhe_aluno.html'
    context_object_name = 'aluno'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['treinos'] = Treino.objects.filter(aluno=self.object)

        context['medidas'] = Medidas.objects.filter(
            aluno=self.object
        ).order_by('-dataMedida')

        return context