from rest_framework import serializers
from .models import Estacionamento,Vagas


class EstacionamentoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Estacionamento
        fields = ['vaga_Ocupada', 'placa', 'horario_Entrada', 'horario_Saida_Estimada','horario_Saida']

class VagasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vagas
        fields = ['vaga']  

