from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from cadastros.models import Aluno
from medidas.models import Medidas

# Create your views here.


class MedidasCreate(CreateView):
    model = Medidas
    fields = ['altura','peso', 'cintura', 'quadril', 'bracoDireito', 'bracoEsquerdo', 'coxaDireita', 'coxaEsquerda', 'panturrilhaDireita', 'panturrilhaEsquerda', 'peito', 'dataMedida']
    template_name = 'form.html'

    def form_valid(self, form):
        aluno = Aluno.objects.get(pk=self.kwargs['pk'])
        form.instance.aluno = aluno
        return super().form_valid(form)
    def get_success_url(self):

        return reverse_lazy('detalhe-aluno', kwargs={'pk': self.kwargs['pk']})
        
        

############################## UPDATE #########################################

class MedidasUpdate(UpdateView):
    model = Medidas
    fields = ['aluno', 'altura','peso', 'cintura', 'quadril', 'bracoDireito', 'bracoEsquerdo', 'coxaDireita', 'coxaEsquerda', 'panturrilhaDireita', 'panturrilhaEsquerda', 'peito', 'dataMedida']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')


############################## DELETE #########################################

class MedidasDelete(DeleteView):
    model = Medidas
    fields = ['aluno', 'altura','peso', 'cintura', 'quadril', 'bracoDireito', 'bracoEsquerdo', 'coxaDireita', 'coxaEsquerda', 'panturrilhaDireita', 'panturrilhaEsquerda', 'peito', 'dataMedida']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')