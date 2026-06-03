from django.contrib import admin
# Importar as classe
from .models import Estado, Cidade, Pessoa
# Register your models here.
admin.site.register(Estado)
admin.site.register(Cidade)
admin.site.register(Pessoa)
