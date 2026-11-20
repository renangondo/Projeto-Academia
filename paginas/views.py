from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
from agenda.utils import montar_semana, proxima_aula
from medidas.models import Medidas
from medidas.utils import calcular_imc, calcular_variacoes, classificar_imc
from agenda.models import HorarioAula
from agenda.utils import montar_semana
from cadastros.models import Pessoa
from exercicio.models import Treino
from agenda.utils import ABREVIACOES, montar_semana, proxima_aula


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
                aluno__professor=pessoa
            ).count()

        elif pessoa and user.groups.filter(name="Aluno").exists():
            horarios = HorarioAula.objects.filter(
                aluno=pessoa
            ).select_related('professor', 'treino')
            context['semana'] = montar_semana(horarios)
            context['proxima_aula'] = proxima_aula(horarios)

            medidas = list(
                Medidas.objects.filter(aluno=pessoa).order_by('-data_medida', '-id')[:2]
            )
            if medidas:
                atual = medidas[0]
                anterior = medidas[1] if len(medidas) > 1 else None
                imc = calcular_imc(atual.peso, atual.altura)

                context['medida_atual'] = atual
                context['imc'] = imc
                context['imc_classificacao'] = classificar_imc(imc)
                context['variacoes'] = calcular_variacoes(atual, anterior)

            hoje = timezone.localdate()

            treinos_atuais = list(
                Treino.objects.filter(
                    aluno=pessoa, data_inicio__lte=hoje, data_fim__gte=hoje
                ).annotate(
                    qtd_exercicios=Count('exercicio_do_treino')
                ).order_by('nome_treino', 'id')
            )

            # em quais dias da semana cada treino aparece na agenda
            dias_por_treino = {}
            for h in horarios:
                if h.treino_id:
                    dias = dias_por_treino.setdefault(h.treino_id, [])
                    abreviacao = ABREVIACOES[h.dia_semana]
                    if abreviacao not in dias:
                        dias.append(abreviacao)

            proxima = context['proxima_aula']
            treino_proximo = proxima['horario'].treino_id if proxima else None

            for t in treinos_atuais:
                t.dias_semana = dias_por_treino.get(t.pk, [])
                t.eh_proximo = (t.pk == treino_proximo)

            # o treino da próxima aula primeiro; os demais em ordem alfabética
            treinos_atuais.sort(key=lambda t: (not t.eh_proximo, t.nome_treino))

            context['treinos_atuais'] = treinos_atuais
            context['treinos_visiveis'] = treinos_atuais[:4]
            context['treinos_restantes'] = treinos_atuais[4:]

        return context