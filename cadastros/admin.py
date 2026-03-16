from django.contrib import admin
# Importar as classe
from .models import Estado, Cidade, Professor, Aluno
# Register your models here.
admin.site.register(Estado)
admin.site.register(Cidade)
admin.site.register(Professor)
admin.site.register(Aluno)
