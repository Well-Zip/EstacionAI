from rest_framework import viewsets
from .serializers import *
from .models import *
class EstacionamentoViewsets(viewsets.ModelViewSet):
    serializer_class = EstacionamentoSerializers
    queryset = Estacionamento.objects.all()

class VagasViewSet(viewsets.ModelViewSet):
    queryset = Vagas.objects.all()
    serializer_class = VagasSerializer





