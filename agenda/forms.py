# agenda/forms.py
from django import forms
from cadastros.models import Pessoa
from .models import HorarioAula


class HorarioAulaForm(forms.ModelForm):
    class Meta:
        model = HorarioAula
        fields = ['aluno', 'dia_semana', 'horario']
        widgets = {
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, professor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.professor = professor

        if professor:
            self.instance.professor = professor
            self.fields['aluno'].queryset = Pessoa.objects.filter(tipo="ALUNO", professor=professor)