import re
import unicodedata

from braces.views import GroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django import forms
from django.utils import timezone
from medidas.utils import calcular_variacoes
from exercicio.models import Treino
from medidas.models import Medidas

from .models import (
    Cidade,
    Estado,
    Pessoa,
    TransferenciaAluno,
    expirar_transferencias_vencidas,
)
from .permissoes import (
    SomenteDoMeuAlunoMixin,
    SomenteMeuPerfilProfessorMixin,
    alunos_do_usuario,
)


############################## AUXILIARES #########################################

MSG_PENDENTE = (
    "Já existe uma solicitação de transferência pendente para esse aluno. "
    "Aguarde a resposta ou o prazo de 48h expirar."
)


def tem_transferencia_pendente(aluno):
    expirar_transferencias_vencidas()   # vencidas (48h) deixam de contar como pendentes
    return TransferenciaAluno.objects.filter(aluno=aluno, status='PENDENTE').exists()


def normalizar_texto(texto):
    """minúsculas e sem acento, para 'joao' achar 'João'."""
    texto = unicodedata.normalize('NFD', (texto or '').lower())
    return ''.join(c for c in texto if unicodedata.category(c) != 'Mn')

class DataNascimentoMixin:
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'data_nascimento' in form.fields:
            form.fields['data_nascimento'].widget = forms.DateInput(
                attrs={'type': 'date', 'max': timezone.localdate().isoformat()},
                format='%Y-%m-%d',
            )
        return form


############################## CREATE #########################################

class EstadoCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Estado
    group_required = "Administrador"
    fields = ['nome', 'sigla']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class CidadeCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Cidade
    group_required = "Administrador"
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class CadastroProfessorCreate(DataNascimentoMixin, CreateView):
    model = Pessoa
    fields = ['nome', 'data_nascimento', 'cpf', 'telefone', 'sexo', 'cidade']
    template_name = 'cadastros/cadastro_professor.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        cpf = form.cleaned_data["cpf"]

        if User.objects.filter(username=cpf).exists():
            form.add_error("cpf", "Já existe um usuário com este CPF.")
            return self.form_invalid(form)

        with transaction.atomic():
            usuario = User.objects.create_user(username=cpf, password=cpf)
            grupo, _ = Group.objects.get_or_create(name="Professor")
            usuario.groups.add(grupo)

            form.instance.precisa_trocar_senha = True
            form.instance.usuario = usuario
            form.instance.tipo = "PROFESSOR"
            return super().form_valid(form)


class AlunoCreate(DataNascimentoMixin, LoginRequiredMixin, GroupRequiredMixin, CreateView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor"]
    fields = ["nome", "data_nascimento", "cpf", "telefone", "objetivo", "sexo", "nivel", "cidade"]
    template_name = "cadastros/form.html"
    success_url = reverse_lazy("listar-aluno")

    def form_valid(self, form):
        cpf = form.cleaned_data["cpf"]

        if User.objects.filter(username=cpf).exists():
            form.add_error("cpf", "Já existe um usuário cadastrado com esse CPF.")
            return self.form_invalid(form)

        with transaction.atomic():
            usuario = User.objects.create_user(username=cpf, password=cpf)
            grupo, _ = Group.objects.get_or_create(name="Aluno")
            usuario.groups.add(grupo)

            form.instance.precisa_trocar_senha = True
            form.instance.usuario = usuario
            form.instance.tipo = "ALUNO"
            form.instance.professor = self.request.user.pessoa_usuario
            return super().form_valid(form)


class TransferenciaCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = TransferenciaAluno
    fields = ['aluno', 'professor_novo', 'observacao']
    template_name = 'cadastros/form_transferencia_professor.html'
    group_required = ["Professor"]

    def get_form(self, form_class=None):
        expirar_transferencias_vencidas()
        form = super().get_form(form_class)
        pessoa = self.request.user.pessoa_usuario

        form.fields['aluno'].queryset = Pessoa.objects.filter(tipo="ALUNO", professor=pessoa)
        form.fields['professor_novo'].queryset = Pessoa.objects.filter(
            tipo="PROFESSOR"
        ).exclude(pk=pessoa.pk)
        return form

    def form_valid(self, form):
        if tem_transferencia_pendente(form.cleaned_data['aluno']):
            form.add_error(None, MSG_PENDENTE)
            return self.form_invalid(form)

        form.instance.professor_atual = self.request.user.pessoa_usuario
        form.instance.origem = 'PROFESSOR'
        form.instance.status = 'PENDENTE'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('minhas-transferencias')


class TransferenciaSolicitarAluno(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = TransferenciaAluno
    fields = ['professor_novo', 'observacao']
    template_name = 'cadastros/form_transferencia_aluno.html'
    group_required = ["Aluno"]

    def get_form(self, form_class=None):
        expirar_transferencias_vencidas()
        form = super().get_form(form_class)
        pessoa = self.request.user.pessoa_usuario

        # preenchido aqui (e não no form_valid) porque o clean() do model
        # precisa do aluno durante a validação
        form.instance.aluno = pessoa
        form.instance.professor_atual = pessoa.professor
        form.instance.origem = 'ALUNO'
        form.instance.status = 'PENDENTE'

        qs = Pessoa.objects.filter(tipo="PROFESSOR")
        if pessoa.professor:
            qs = qs.exclude(pk=pessoa.professor.pk)
        form.fields['professor_novo'].queryset = qs

        return form

    def form_valid(self, form):
        if tem_transferencia_pendente(form.instance.aluno):
            form.add_error(None, MSG_PENDENTE)
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('minhas-solicitacoes')


############################## UPDATE #########################################

class EstadoUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Estado
    group_required = "Administrador"
    fields = ['nome', 'sigla']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class CidadeUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Cidade
    group_required = "Administrador"
    fields = ['nome', 'estado']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class ProfessorUpdate(DataNascimentoMixin, SomenteMeuPerfilProfessorMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor"]
    fields = ['nome', 'data_nascimento', 'telefone', 'sexo', 'cidade']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


class AlunoUpdate(DataNascimentoMixin, SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    campo_aluno = "pk"
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador", "Professor", "Aluno"]
    fields = ['nome', 'data_nascimento', 'telefone', 'objetivo', 'sexo', 'nivel', 'cidade']
    template_name = 'cadastros/form.html'
    success_url = reverse_lazy('inicio')


############################## DELETE #########################################

class EstadoDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Estado
    group_required = "Administrador"
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


class CidadeDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Cidade
    group_required = "Administrador"
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('inicio')


class ProfessorDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    login_url = reverse_lazy('login')
    model = Pessoa
    group_required = ["Administrador"]      # professor não exclui professor
    template_name = 'cadastros/form-excluir.html'
    success_url = reverse_lazy('listar-professor')


class AlunoDelete(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    campo_aluno = "pk"
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


class AlunoList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Pessoa
    template_name = "cadastros/listar_alunos.html"
    context_object_name = 'pessoa_list'
    group_required = ["Professor", "Administrador"]

    def get_queryset(self):
        alunos = alunos_do_usuario(self.request.user).select_related(
            'professor', 'cidade'
        ).order_by('nome')

        busca = self.request.GET.get('q', '').strip()
        if not busca:
            return alunos

        termo = normalizar_texto(busca)
        digitos = re.sub(r'[\s.\-()]', '', busca)
        busca_numerica = digitos.isdigit()

        def combina(aluno):
            if termo in normalizar_texto(f"{aluno.nome} {aluno.objetivo or ''}"):
                return True
            if busca_numerica:
                return digitos in aluno.cpf or digitos in aluno.telefone
            return False

        return [a for a in alunos if combina(a)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busca'] = self.request.GET.get('q', '').strip()
        return context


class ProfessorList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    login_url = reverse_lazy('login')
    model = Pessoa
    template_name = "cadastros/listar_professores.html"
    group_required = ["Administrador"]

    def get_queryset(self):
        return Pessoa.objects.filter(tipo="PROFESSOR")


class MinhasTransferenciasList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = TransferenciaAluno
    template_name = 'cadastros/listar_transferencias.html'
    context_object_name = 'transferencias'
    group_required = ["Professor"]

    def get_queryset(self):
        expirar_transferencias_vencidas()
        pessoa = self.request.user.pessoa_usuario
        return TransferenciaAluno.objects.filter(
            Q(professor_atual=pessoa) | Q(professor_novo=pessoa)
        ).order_by('-cadastrado_em')


class MinhasSolicitacoesAlunoList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = TransferenciaAluno
    template_name = 'cadastros/listar_transferencias.html'
    context_object_name = 'transferencias'
    group_required = ["Aluno"]

    def get_queryset(self):
        expirar_transferencias_vencidas()
        pessoa = self.request.user.pessoa_usuario
        return TransferenciaAluno.objects.filter(aluno=pessoa).order_by('-cadastrado_em')


############################## RESPOSTA DA TRANSFERÊNCIA ######################

class TransferenciaResponder(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ["Professor"]

    def post(self, request, pk):
        expirar_transferencias_vencidas()
        transferencia = get_object_or_404(TransferenciaAluno, pk=pk)
        pessoa = request.user.pessoa_usuario

        if transferencia.professor_novo != pessoa:
            return HttpResponseForbidden("Você não pode responder essa transferência.")

        if transferencia.status != 'PENDENTE':
            return redirect('minhas-transferencias')

        acao = request.POST.get('acao')

        if acao == 'aceitar':
            transferencia.status = 'ACEITA'
            transferencia.aluno.professor = pessoa
            transferencia.aluno.save()
        elif acao == 'recusar':
            transferencia.status = 'RECUSADA'

        transferencia.save()
        return redirect('minhas-transferencias')


############################## DETAIL #########################################

class PessoaDetail(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, DetailView):
    campo_aluno = "pk"
    login_url = reverse_lazy('login')
    model = Pessoa
    context_object_name = "aluno"
    template_name = "cadastros/detalhe_aluno.html"
    group_required = ["Professor", "Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["treinos"] = Treino.objects.filter(aluno=self.object)

        # só as duas últimas medidas (a mais recente primeiro)
        medidas = list(
            Medidas.objects.filter(aluno=self.object).order_by("-data_medida", "-id")[:2]
        )

        for medida in medidas:
            medida.variacoes = {}

        if len(medidas) == 2:
            medidas[0].variacoes = calcular_variacoes(medidas[0], medidas[1])

        context["medidas"] = medidas
        return context


class MeuPerfilView(LoginRequiredMixin, TemplateView):
    template_name = 'cadastros/meu_perfil.html'