from django.contrib import admin
from .models import Categoria, Treino, Exercicio, ExercicioTreino

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Treino)
admin.site.register(Exercicio)
admin.site.register(ExercicioTreino)