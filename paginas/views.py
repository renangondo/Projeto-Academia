from django.views.generic import TemplateView

from cadastros.models import Aluno, Cidade, Estado, Professor

# Create your views here.

class PaginaModelo(TemplateView):
    template_name ="modelo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_alunos'] = Aluno.objects.count()
        context['total_professores'] = Professor.objects.count()
        context['total_cidades'] = Cidade.objects.count()
        context['total_estados'] = Estado.objects.count()
        context['ultimos_alunos'] = Aluno.objects.order_by('-id')[:5]
        
