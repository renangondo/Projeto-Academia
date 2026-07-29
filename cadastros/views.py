from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import DetailView

from django.contrib import messages

from exercicio.models import Treino
from medidas.models import Medidas
from django.contrib.auth.models import Group, User
from .models import Cidade, Estado, Pessoa
from django.urls import reverse_lazy

# Importar o mixin de login e grupo
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin

# Create your views here.

####CREATE VIEW#####
class EstadoCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Estado  # Qual modelo que será cadastrado
    group_required = "Administrador"
    fields = ['nome', 'sigla'] # Quais campos que irá aparecer para cadastrar
    template_name = 'cadastros/form.html' # Qual template será usado
    success_url = reverse_lazy('inicio') # Onde será redirecionado


class CidadeCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Cidade
    group_required = "Administrador"
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')



class CadastroProfessorCreate(CreateView):
    model = Pessoa
    group_required = ["Administrador", "Professor"]
    fields = ['nome', 'idade', 'cpf', 'telefone', 'sexo', 'cidade']
    template_name = 'cadastros/cadastro_professor.html'
    success_url = reverse_lazy = ('login')

    def form_valid(self, form):

        cpf = form.cleaned_data["cpf"]

        if User.objects.filter(username=cpf).exists():
            form.add.error("cpf", "Já existe um usuario com este CPF")
            return self.form_invalid(form)

        usuario = User.objects.create_user(
            username=form.cleaned_data["cpf"],
            password=form.cleaned_data["cpf"]
        )

        grupo, created = Group.objects.get_or_create(name="Professor")
        usuario.groups.add(grupo)

        form.instance.usuario = usuario
        form.instance.tipo = "PROFESSOR"

        return super().form_valid(form)


class AlunoCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor"]
    fields = ["nome", "idade", "cpf", "telefone", "objetivo", "sexo", "nivel", "cidade"]
    template_name = "cadastros/form.html"
    success_url = reverse_lazy("listar-aluno")


    def form_valid(self, form):

        cpf = form.cleaned_data["cpf"]

        if User.objects.filter(username=cpf).exists():
            form.add_error("cpf", "Já existe um usuário cadastrado com esse CPF.")
            return self.form_invalid(form)

        usuario = User.objects.create_user(
            username=cpf,
            password=cpf
        )

        grupo, created = Group.objects.get_or_create(name="Aluno")
        usuario.groups.add(grupo)

        form.instance.usuario = usuario
        form.instance.tipo = "ALUNO"
        form.instance.professor = self.request.user.pessoa_usuario

        return super().form_valid(form)

############################## UPDATE #########################################

class EstadoUpdate(LoginRequiredMixin,GroupRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Estado
    group_required = "Administrador"
    fields= ['nome', 'sigla']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')

class CidadeUpdate(LoginRequiredMixin,GroupRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Cidade
    group_required = "Administrador"
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class ProfessorUpdate(LoginRequiredMixin,GroupRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor"]
    fields = ['nome', 'idade','telefone', 'sexo','cidade']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class AlunoUpdate(LoginRequiredMixin,GroupRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor", "Aluno"]
    fields = ['nome', 'idade', 'telefone', 'objetivo', 'sexo', 'nivel','cidade']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')

############################## DELETE #########################################

class EstadoDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Estado
    group_required = "Admistrador"
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


class CidadeDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Cidade
    group_required = "Admistrador"
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


class ProfessorDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor"]
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-professor')

class AlunoDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor"]
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-aluno')


############################## LISTAR #########################################

class EstadoList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Estado
    template_name = 'cadastros/listar_estado.html'

    group_required = ["Administrador"]


class CidadeList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Cidade
    template_name = 'cadastros/listar_cidades.html'

    group_required = ["Administrador"]


class PessoaList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Pessoa
    template_name = 'cadastros/listar_alunos.html'

    # Sobrescrever o método get_queryset para personalizar a consulta
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Se o usuário for do grupo "Administrador", liste tudo
        if self.request.user.groups.filter(name='Administrador').exists():
            return queryset
        # Se não, liste apenas as pessoas associadas ao professor
        else:
            return queryset.filter(professor=self.request.user)

class AlunoList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Pessoa
    template_name = "cadastros/listar_alunos.html"

    group_required = ["Professor", "Administrador"]

    def get_queryset(self):

        queryset = Pessoa.objects.filter(tipo="ALUNO")

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(
            professor=self.request.user.pessoa_usuario
        )


class ProfessorList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Pessoa
    template_name = "cadastros/listar_professores.html"

    group_required = ["Professor", "Administrador"]

    def get_queryset(self):


        return Pessoa.objects.filter(
            tipo="PROFESSOR"
        )


############################## DETAIL #########################################

class PessoaDetail(LoginRequiredMixin, GroupRequiredMixin,DetailView):
    login_url = reverse_lazy('login')
    model = Pessoa
    context_object_name = "aluno"
    template_name = "cadastros/detalhe_aluno.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["treinos"] = Treino.objects.filter(
            aluno=self.object.usuario
        )

        context["medidas"] = Medidas.objects.filter(
            aluno=self.object.usuario
        ).order_by("-data_medida")

        return context