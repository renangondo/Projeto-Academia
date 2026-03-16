from django.views.generic.edit import CreateView
from .models import Cidade, Estado, Professor, Aluno
from django.urls import reverse_lazy

# Create your views here.

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
    fields = ['nome', 'idade', 'cpf', 'telefone', 'obejtico', 'data_criacao', 'sexo', 'nivel', 'cidade' 'professor']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')
