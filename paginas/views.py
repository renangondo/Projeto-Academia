from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from agenda.models import HorarioAula
from agenda.utils import montar_semana
from cadastros.models import Pessoa
from exercicio.models import Treino


class InicioView(LoginRequiredMixin, TemplateView):
    template_name = "paginas/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        pessoa = getattr(user, 'pessoa_usuario', None)

        if pessoa and user.groups.filter(name="Professor").exists():
            horarios = HorarioAula.objects.filter(
                professor=pessoa
            ).select_related('aluno', 'treino')
            context['semana'] = montar_semana(horarios)

            context['total_alunos'] = Pessoa.objects.filter(
                tipo="ALUNO", professor=pessoa
            ).count()
            context['total_treinos'] = Treino.objects.filter(
                cadastrado_por=pessoa
            ).count()

        elif pessoa and user.groups.filter(name="Aluno").exists():
            horarios = HorarioAula.objects.filter(
                aluno=pessoa
            ).select_related('professor', 'treino')
            context['semana'] = montar_semana(horarios)

        return context