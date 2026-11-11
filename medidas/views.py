from django import forms
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.views.generic import TemplateView
from .utils import calcular_imc, classificar_imc
from cadastros.permissoes import SomenteDoMeuAlunoMixin, alunos_do_usuario, eh_aluno
from medidas.models import Medidas

CAMPOS = ['altura', 'peso', 'cintura', 'quadril', 'braco_direito', 'braco_esquerdo',
          'coxa_direita', 'coxa_esquerda', 'panturrilha_direita', 'panturrilha_esquerda',
          'peito', 'data_medida']


class RetornoMedidasMixin:
    def get_success_url(self):
        user = self.request.user
        if eh_aluno(user) and not user.is_superuser:
            return reverse_lazy('inicio')   # aluno não tem tela de detalhe do aluno
        return reverse_lazy('detalhe-aluno', kwargs={'pk': self.object.aluno_id})


class FormMedidasMixin:
    template_name = 'medidas/form_medida.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # seletor de data do navegador (e a data de hoje já preenchida)
        form.fields['data_medida'].widget = forms.DateInput(
            attrs={'type': 'date'}, format='%Y-%m-%d'
        )
        return form


class MedidasCreate(FormMedidasMixin, RetornoMedidasMixin, LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Medidas
    fields = CAMPOS
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_form_kwargs(self):
        # 404 se o aluno não existir ou não for acessível por esse usuário
        self.aluno = get_object_or_404(alunos_do_usuario(self.request.user), pk=self.kwargs['pk'])
        return super().get_form_kwargs()

    def get_ultima(self):
        if not hasattr(self, '_ultima'):
            self._ultima = Medidas.objects.filter(
                aluno=self.aluno
            ).order_by('-data_medida', '-id').first()
        return self._ultima

    def get_initial(self):
        initial = super().get_initial()

        ultima = self.get_ultima()
        if ultima:
            for campo in CAMPOS:
                if campo not in ('data_medida', 'altura'):
                    initial[campo] = getattr(ultima, campo)

        initial['data_medida'] = timezone.localdate()
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.get_ultima():
            form.fields.pop('altura')   # a altura é mantida da última medida
        return form

    def form_valid(self, form):
        form.instance.aluno = self.aluno
        form.instance.cadastrado_por = self.request.user

        ultima = self.get_ultima()
        if ultima:
            form.instance.altura = ultima.altura

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aluno'] = self.aluno
        context['ultima'] = self.get_ultima()
        return context


class MedidasUpdate(FormMedidasMixin, SomenteDoMeuAlunoMixin, RetornoMedidasMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Medidas
    fields = CAMPOS          # aqui a altura continua editável, para corrigir um erro
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['aluno'] = self.object.aluno
        return context


class MedidasDelete(SomenteDoMeuAlunoMixin, RetornoMedidasMixin, LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Medidas
    template_name = 'form-excluir.html'
    group_required = ["Professor", "Administrador", "Aluno"]


##################################################################################

CAMPOS_SERIE = ['peso', 'cintura', 'quadril', 'braco_direito', 'braco_esquerdo',
                'coxa_direita', 'coxa_esquerda', 'panturrilha_direita',
                'panturrilha_esquerda', 'peito']

class EvolucaoMedidasView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'medidas/evolucao.html'
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        aluno = get_object_or_404(alunos_do_usuario(self.request.user), pk=self.kwargs['pk'])
        medidas = list(Medidas.objects.filter(aluno=aluno).order_by('data_medida', 'id'))

        context['aluno'] = aluno
        context['historico'] = list(reversed(medidas))
        context['serie_json'] = [
            {
                'data': m.data_medida.strftime('%d/%m/%Y'),
                'imc': calcular_imc(m.peso, m.altura),
                **{campo: getattr(m, campo) for campo in CAMPOS_SERIE},
            }
            for m in medidas
        ]

        if medidas:
            atual = medidas[-1]
            anterior = medidas[-2] if len(medidas) > 1 else None
            imc = calcular_imc(atual.peso, atual.altura)

            def variacao(campo):
                if anterior is None:
                    return None
                return round(getattr(atual, campo) - getattr(anterior, campo), 1)

            context['resumo'] = {
                'atual': atual,
                'imc': imc,
                'classificacao': classificar_imc(imc),
                'var_peso': variacao('peso'),
                'var_cintura': variacao('cintura'),
                'total': len(medidas),
            }

        return context