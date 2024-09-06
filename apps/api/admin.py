from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(historico_Estacionamento)
class historico_EstacionamentoAdmin(admin.ModelAdmin):
    list_display = ('vaga_Ocupada','placa','horario_Entrada','horario_Saida','tempo_Estacionado',)
    list_filter = ('vaga_Ocupada','placa','horario_Entrada','horario_Saida')

@admin.register(Estacionamento)
class historico_EstacionamentoAdmin(admin.ModelAdmin):
    list_display = ('vaga_Ocupada','placa','horario_Entrada','horario_Saida_Estimada','horario_Saida')
    list_filter = ('vaga_Ocupada','placa','horario_Entrada')

admin.site.register(Vagas)
