from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from medidas.models import Medidas

# Create your views here.


class MedidasCreate(CreateView):
    model = Medidas
    fields = ['altura', 'peso', 'cintura', 'quadril', 'braco_direito', 'braco_esquerdo', 'coxa_direita', 'coxa_esquerda', 'panturrilha_direita', 'panturrilha_esquerda', 'peito', 'data_medida']
    template_name = 'form.html'

    def form_valid(self, form):
        aluno = User.objects.get(pk=self.kwargs['pk'])
        form.instance.aluno = aluno
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('detalhe-aluno', kwargs={'pk': self.kwargs['pk']})
        
        

############################## UPDATE #########################################

class MedidasUpdate(UpdateView):
    model = Medidas
    fields = ['aluno', 'altura', 'peso', 'cintura', 'quadril', 'braco_direito', 'braco_esquerdo', 'coxa_direita', 'coxa_esquerda', 'panturrilha_direita', 'panturrilha_esquerda', 'peito', 'data_medida']
    template_name = 'form.html'
    success_url = reverse_lazy('inicio')


############################## DELETE #########################################

class MedidasDelete(DeleteView):
    model = Medidas
    fields = ['aluno', 'altura', 'peso', 'cintura', 'quadril', 'braco_direito', 'braco_esquerdo', 'coxa_direita', 'coxa_esquerda', 'panturrilha_direita', 'panturrilha_esquerda', 'peito', 'data_medida']
    template_name = 'form-excluir.html'
    success_url = reverse_lazy('inicio')