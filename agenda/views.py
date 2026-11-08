from django.shortcuts import render

from django.views.generic import CreateView, ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin

from .models import HorarioAula
from .forms import HorarioAulaForm


############################## CREATE #########################################

class HorarioAulaCreate(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = HorarioAula
    form_class = HorarioAulaForm
    template_name = 'agenda/form_horario.html'
    group_required = ["Professor"]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['professor'] = self.request.user.pessoa_usuario
        return kwargs

    def get_success_url(self):
        return reverse_lazy('minha-agenda')

    
    def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['treinos_json'] = [
        {"id": t.pk, "nome": t.nome_treino, "aluno": t.aluno_id}
        for t in context['form'].fields['treino'].queryset
    ]
    return context

############################## LISTAR #########################################

class AgendaProfessorList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = HorarioAula
    template_name = 'agenda/agenda_professor.html'
    context_object_name = 'horarios'
    group_required = ["Professor"]

    def get_queryset(self):
        return HorarioAula.objects.filter(
            professor=self.request.user.pessoa_usuario
        ).select_related('aluno')


class AgendaAlunoList(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = HorarioAula
    template_name = 'agenda/agenda_aluno.html'
    context_object_name = 'horarios'
    group_required = ["Aluno"]

    def get_queryset(self):
        return HorarioAula.objects.filter(
            aluno=self.request.user.pessoa_usuario
        ).select_related('professor')

############################## DELETAR #########################################

class HorarioAulaDelete(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = HorarioAula
    template_name = 'agenda/form-excluir.html'
    success_url = reverse_lazy('minha-agenda')
    group_required = ["Professor"]

    def get_queryset(self):
        # garante que um professor só consiga excluir horário dele mesmo
        return HorarioAula.objects.filter(professor=self.request.user.pessoa_usuario)

############################## UPDATE #########################################

class HorarioTreinoUpdate(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = HorarioAula
    fields = ['treino']
    template_name = 'cadastros/form.html'
    group_required = ["Professor"]

    def get_queryset(self):
        return HorarioAula.objects.filter(professor=self.request.user.pessoa_usuario)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['treino'].queryset = Treino.objects.filter(aluno=self.object.aluno)
        return form

    def get_success_url(self):
        return reverse_lazy('minha-agenda')