from django.views.generic import TemplateView

from cadastros.models import Cidade, Estado, Pessoa

# Create your views here.

class PaginaModelo(TemplateView):
    template_name ="modelo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_pessoas'] = Pessoa.objects.count()
        context['total_cidades'] = Cidade.objects.count()
        context['total_estados'] = Estado.objects.count()
        
