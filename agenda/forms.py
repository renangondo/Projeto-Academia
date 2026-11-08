# agenda/forms.py
from django import forms
from cadastros.models import Pessoa
from .models import HorarioAula
from exercicio.models import Treino


class HorarioAulaForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        fields = ['aluno', 'treino', 'dia_semana', 'horario']
        widgets = {
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {'treino': 'Treino da aula (opcional)'}

    def __init__(self, *args, professor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.professor = professor

        if professor:
            self.instance.professor = professor
            self.fields['aluno'].queryset = Pessoa.objects.filter(tipo="ALUNO", professor=professor)
            self.fields['treino'].queryset = Treino.objects.filter(
                aluno__professor=professor
            ).order_by('-cadastrado_em')