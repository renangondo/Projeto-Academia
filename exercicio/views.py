from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django import forms
from cadastros.models import Pessoa
from .models import Categoria, Treino, Exercicio, ExercicioTreino
from django.views.generic import DetailView, ListView
from django.urls import reverse_lazy
from django.db.models import Count, ProtectedError
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Q, Count, ProtectedError
from django.utils import timezone
from django.shortcuts import get_object_or_404
from cadastros.permissoes import SomenteDoMeuAlunoMixin, alunos_do_usuario
from .compartilhar import montar_link_whatsapp
from django.http import HttpResponse
from django.utils.text import slugify
from django.views.generic import TemplateView
from .cargas import registrar_carga
from .models import HistoricoCarga   # junto do import de models que você já tem
from .pdf import gerar_pdf_treino
import unicodedata
from cadastros.permissoes import SomenteDoMeuAlunoMixin, alunos_do_usuario, eh_admin   # inclua o eh_admin
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

def normalizar(texto):
    """minúsculas e sem acento, para 'agachamento' achar 'Agachamento'."""
    texto = unicodedata.normalize('NFD', (texto or '').lower())
    return ''.join(c for c in texto if unicodedata.category(c) != 'Mn')


def do_catalogo(usuario):
    """Exercício do catálogo geral = criado por um administrador."""
    return usuario.is_superuser or any(g.name == "Administrador" for g in usuario.groups.all())


def destino_exercicios(user, categoria_id):
    """Admin volta para a lista da categoria; professor volta para a sua lista."""
    if eh_admin(user):
        return reverse_lazy('listar-exercicio-categoria', kwargs={'pk': categoria_id})
    return reverse_lazy('listar-exercicio')

############################## A MAIS #########################################
class DatasTreinoMixin:
    """Mostra o seletor de data do navegador nos campos de início e encerramento."""
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for campo in ('data_inicio', 'data_fim'):
            if campo in form.fields:
                form.fields[campo].widget = forms.DateInput(
                    attrs={'type': 'date'}, format='%Y-%m-%d'
                )
        return form
    
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


class TreinoCreate(DatasTreinoMixin, LoginRequiredMixin, GroupRequiredMixin, CreateView):
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

        initial.setdefault('data_inicio', timezone.localdate())
        
        return initial
                    
    
    def form_valid(self, form):
        form.instance.cadastrado_por = self.request.user.pessoa_usuario
        return super().form_valid(form)
    
    def get_success_url(self):

        return reverse_lazy('detalhe-aluno', kwargs={'pk': self.object.aluno.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['aluno'].queryset = alunos_do_usuario(self.request.user)
        return form
    

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
        return destino_exercicios(self.request.user, self.object.categoria_id)



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

    def get_form_kwargs(self):
        self.treino = get_object_or_404(
            Treino.objects.filter(aluno__in=alunos_do_usuario(self.request.user)),
            pk=self.kwargs['pk'],
        )
        return super().get_form_kwargs()
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['exercicio'].queryset = exercicios_visiveis(self.request.user)
        return form

    def form_valid(self, form):
        form.instance.treino = self.treino
        form.instance.cadastrado_por = self.request.user.pessoa_usuario

        response = super().form_valid(form)

        registrar_carga(
            self.treino.aluno, self.object.exercicio, self.object.peso_atual, self.request.user
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('detalhe-treino', kwargs={'pk': self.kwargs['pk']})

############################## UPDATE #########################################


class CategoriaUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Categoria
    fields = ['nome']
    template_name = 'form.html'
    success_url = reverse_lazy('listar-categoria')
    group_required = ["Administrador"]


class TreinoUpdate(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
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

class ExercicioTreinoUpdate(DatasTreinoMixin, SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    campo_aluno = 'treino__aluno'
    model = ExercicioTreino
    fields = ['exercicio', 'series', 'repeticoes', 'descanso', 'peso_atual']   # sem 'treino'
    template_name = 'form.html'
    group_required = ["Professor", "Administrador"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['exercicio'].queryset = exercicios_visiveis(self.request.user)
        return form

    def get_success_url(self):
        return destino_exercicios(self.request.user, self.object.categoria_id)

    def form_valid(self, form):
        mudou = 'peso_atual' in form.changed_data or 'exercicio' in form.changed_data

        response = super().form_valid(form)

        if mudou:
            registrar_carga(
                self.object.treino.aluno, self.object.exercicio,
                self.object.peso_atual, self.request.user
            )
        return response
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


class TreinoDelete(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, DeleteView):
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
        return destino_exercicios(self.request.user, self.object.categoria_id)

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Não é possível excluir: esse exercício já está sendo usado em treinos."
            )
            return HttpResponseRedirect(self.get_success_url())

class ExercicioTreinoDelete(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    campo_aluno = 'treino__aluno'
    model = ExercicioTreino
    template_name = 'form-excluir.html'
    group_required = ["Professor", "Administrador"]

    def get_success_url(self):
        return reverse_lazy('detalhe-treino', kwargs={'pk': self.object.treino_id})


############################## DETAIL #########################################




class TreinoDetail(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Treino
    template_name = 'detalhe_treino.html'
    context_object_name = 'treino'
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        exercicios = ExercicioTreino.objects.filter(
            treino=self.object
        ).select_related('exercicio', 'exercicio__categoria').order_by('cadastrado_em', 'id')

        context['exercicios_treino'] = exercicios
        context['link_whatsapp'] = montar_link_whatsapp(self.object, exercicios)
        return context

############################## LIST #########################################
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


class TreinoList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Treino
    template_name = 'listar_treino.html'
    context_object_name = 'treinos'
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_queryset(self):
        hoje = timezone.localdate()

        qs = Treino.objects.filter(
            aluno__in=alunos_do_usuario(self.request.user)
        ).select_related('aluno').annotate(
            qtd_exercicios=Count('exercicio_do_treino')
        )

        busca = self.request.GET.get('q', '').strip()
        if busca:
            qs = qs.filter(
                Q(nome_treino__icontains=busca) | Q(aluno__nome__icontains=busca)
            )

        situacao = self.request.GET.get('situacao', '')
        if situacao == 'andamento':
            qs = qs.filter(data_inicio__lte=hoje, data_fim__gte=hoje)
        elif situacao == 'futuros':
            qs = qs.filter(data_inicio__gt=hoje)
        elif situacao == 'encerrados':
            qs = qs.filter(data_fim__lt=hoje)

        if self.request.GET.get('ordem') == 'antigos':
            return qs.order_by('data_inicio', 'id')
        return qs.order_by('-data_inicio', '-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busca'] = self.request.GET.get('q', '')
        context['situacao'] = self.request.GET.get('situacao', '')
        context['ordem'] = self.request.GET.get('ordem', 'recentes')
        return context


class ExercicioList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Exercicio
    template_name = 'listar_exercicio.html'
    context_object_name = 'exercicios'
    group_required = ["Professor", "Administrador"]

    def get_origem(self):
        return self.request.GET.get('origem') or ('todos' if eh_admin(self.request.user) else 'meus')

    def get_queryset(self):
        user = self.request.user
        pessoa = getattr(user, 'pessoa_usuario', None)
        origem = self.get_origem()

        qs = exercicios_visiveis(user).select_related(
            'categoria', 'cadastrado_por__usuario'
        ).prefetch_related('cadastrado_por__usuario__groups')

        if origem == 'meus':
            qs = qs.filter(cadastrado_por=pessoa) if pessoa else qs.none()
        elif origem == 'catalogo':
            qs = qs.filter(
                Q(cadastrado_por__usuario__is_superuser=True)
                | Q(cadastrado_por__usuario__groups__name="Administrador")
            ).distinct()

        categoria = self.request.GET.get('categoria', '')
        if categoria.isdigit():
            qs = qs.filter(categoria_id=categoria)

        lista = list(qs.order_by('categoria__nome', 'nome'))

        busca = self.request.GET.get('q', '').strip()
        if busca:
            termo = normalizar(busca)
            lista = [e for e in lista if termo in normalizar(e.nome)]

        for e in lista:
            e.do_catalogo = do_catalogo(e.cadastrado_por.usuario)

        return lista

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['origem'] = self.get_origem()
        context['busca'] = self.request.GET.get('q', '').strip()
        context['categoria_sel'] = self.request.GET.get('categoria', '')
        context['categorias'] = Categoria.objects.order_by('nome')
        return context
#################################### CARGA #######################################################
class RegistrarCarga(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    campo_aluno = 'treino__aluno'
    model = ExercicioTreino
    fields = ['peso_atual']
    template_name = 'registrar_carga.html'
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['peso_atual'].label = 'Carga utilizada (kg)'
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        registrar_carga(
            self.object.treino.aluno, self.object.exercicio,
            self.object.peso_atual, self.request.user
        )
        return response

    def get_success_url(self):
        return reverse_lazy('detalhe-treino', kwargs={'pk': self.object.treino_id})


class HistoricoCargaDelete(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    campo_aluno = 'aluno'
    model = HistoricoCarga
    template_name = 'form-excluir.html'
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_success_url(self):
        return reverse_lazy('historico-cargas', kwargs={'pk': self.object.aluno_id})


class HistoricoCargasView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'historico_cargas.html'
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        aluno = get_object_or_404(alunos_do_usuario(self.request.user), pk=self.kwargs['pk'])

        registros = HistoricoCarga.objects.filter(aluno=aluno).select_related(
            'exercicio', 'exercicio__categoria', 'registrado_por'
        ).order_by('data', 'id')

        # ?exercicio=ID mostra só um exercício, com todos os registros
        filtro = self.request.GET.get('exercicio')
        if filtro and filtro.isdigit():
            registros = registros.filter(exercicio_id=filtro)
        else:
            filtro = None

        grupos = {}
        for registro in registros:
            grupos.setdefault(registro.exercicio_id, []).append(registro)

        cartoes = []
        graficos = []

        for regs in grupos.values():
            exercicio = regs[0].exercicio
            inicial, atual = regs[0].carga, regs[-1].carga
            diferenca = round(atual - inicial, 1)

            if diferenca > 0:
                sentido = 'subiu'
            elif diferenca < 0:
                sentido = 'desceu'
            else:
                sentido = 'igual'

            percentual = round(abs(diferenca) / inicial * 100, 1) if inicial else None
            recentes = list(reversed(regs)) if filtro else list(reversed(regs[-5:]))

            cartoes.append({
                'exercicio': exercicio,
                'inicial': inicial,
                'atual': atual,
                'diferenca': abs(diferenca),
                'percentual': percentual,
                'sentido': sentido,
                'total': len(regs),
                'recentes': recentes,
            })
            graficos.append({
                'id': exercicio.pk,
                'serie': [
                    {'data': r.data.strftime('%d/%m/%Y'), 'carga': r.carga}
                    for r in regs[-20:]
                ],
            })

        cartoes.sort(key=lambda c: c['exercicio'].nome)

        context['aluno'] = aluno
        context['cartoes'] = cartoes
        context['graficos_json'] = graficos
        context['filtro'] = filtro
        return context
##################################### PDF ###########################################
class TreinoPDFView(SomenteDoMeuAlunoMixin, LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Treino
    group_required = ["Professor", "Administrador", "Aluno"]

    def get(self, request, *args, **kwargs):
        treino = self.get_object()

        exercicios = ExercicioTreino.objects.filter(
            treino=treino
        ).select_related('exercicio', 'exercicio__categoria').order_by('cadastrado_em', 'id')

        pdf = gerar_pdf_treino(treino, exercicios)
        nome_arquivo = slugify(f'treino {treino.nome_treino} {treino.aluno.nome}') + '.pdf'

        resposta = HttpResponse(pdf, content_type='application/pdf')
        resposta['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        return resposta