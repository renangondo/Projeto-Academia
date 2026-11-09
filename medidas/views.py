from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin

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


class MedidasCreate(RetornoMedidasMixin, LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Medidas
    fields = CAMPOS
    template_name = 'form.html'
    group_required = ["Professor", "Administrador", "Aluno"]

    def get_form_kwargs(self):
        # 404 se o aluno não existir ou não for acessível por esse usuário
        self.aluno = get_object_or_404(alunos_do_usuario(self.request.user), pk=self.kwargs['pk'])
        return super().get_form_kwargs()

    def form_valid(self, form):
        form.instance.aluno = self.aluno
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)


class MedidasUpdate(SomenteDoMeuAlunoMixin, RetornoMedidasMixin, LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Medidas
    fields = CAMPOS          # sem 'aluno': a medida não pode mudar de dono
    template_name = 'form.html'
    group_required = ["Professor", "Administrador", "Aluno"]


class MedidasDelete(SomenteDoMeuAlunoMixin, RetornoMedidasMixin, LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Medidas
    template_name = 'form-excluir.html'
    group_required = ["Professor", "Administrador", "Aluno"]