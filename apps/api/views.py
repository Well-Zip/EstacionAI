import datetime,pytz
import json
from django.utils import timezone

from django.http import Http404, JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Estacionamento,Vagas
from django.shortcuts import get_object_or_404
from .serializers import EstacionamentoSerializers, VagasSerializer

def home(request):
    return render(request, "home.html")


def desocupar_all():
    vagas = Vagas.objects.all()
    for vaga in vagas:
        vaga.em_uso = False 
        vaga.save()





class EstacionamentoCAD(APIView):
    def post(self, request):
        serializer = EstacionamentoSerializers(data=request.data)
        
        if serializer.is_valid():
            try:
                serializer.save()
                vaga = serializer.validated_data.get('vaga_Ocupada')
                return Response({'detail': f'A vaga {vaga} foi ocupada com sucesso.'}, status=status.HTTP_201_CREATED)

            except Exception as e:  # Capture a exceção específica, se possível
                vaga = serializer.validated_data.get('vaga_Ocupada')
                return Response({'detail': f'A vaga {vaga} já está sendo utilizada.'}, status=status.HTTP_409_CONFLICT)
        
        # Caso o serializer não seja válido, retorne um erro
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EstacionamentoDelete(APIView):
    def delete(self, request, vaga):
        try:
            # Tenta encontrar o registro da vaga
            estacionamento = get_object_or_404(Estacionamento, vaga_Ocupada=vaga.upper())
            estacionamento.salvar_historico_deletar_estacionamento()
            return Response({"message": f"A vaga {vaga} foi liberada e salva no histórico."}, status=status.HTTP_200_OK)

        except Http404:
            # Retorna uma resposta personalizada caso a vaga não seja encontrada no banco
            return Response({"error": f"A vaga {vaga} não está ocupada ou nao está cadastrada no sistema."}, status=status.HTTP_404_NOT_FOUND)


class EstacionamentoDeleteAll(APIView):
    def get(self,request):
        desocupar_all()
        return Response({"message": "Todas as vagas foram liberadas"}, status=status.HTTP_200_OK)

    def delete(self, request):
    # Buscar todos os registros de estacionamento
        estacionamentos = Estacionamento.objects.all()
        
        if not estacionamentos.exists():
            return Response({"message": "Nenhuma vaga encontrada para deletar."}, status=status.HTTP_404_NOT_FOUND)

        # Iterar sobre cada estacionamento e salvar o histórico antes de deletar
        for estacionamento in estacionamentos:
            estacionamento.salvar_historico_deletar_estacionamento()  # Salvar histórico e liberar a vaga individualmente
        
       

        # Após salvar o histórico de todos, deletar os registros
        estacionamentos.delete()

        return Response({"message": "Todas as vagas foram liberadas e salvas no histórico."}, status=status.HTTP_200_OK)


class Estacionamento_Info(APIView):
    def put(self, request, vaga):
        estacionamento = get_object_or_404(Estacionamento, vaga_Ocupada=vaga.upper())
        
        estacionamento.horario_Saida_Estimada = estacionamento.horario_Saida_Estimada + datetime.timedelta(minutes=2)
        
        # Salva o objeto com o novo horário de saída estimada
        estacionamento.save()

        return Response({"message": "Data e Hora de Saída Estimada atualizadas com sucesso para 2 minutos a mais."}, status=status.HTTP_200_OK)
    

    def get(self, request, vaga):
        try:
            # Busca o registro da vaga pelo parâmetro 'vaga'
            estacionamento = get_object_or_404(Estacionamento, vaga_Ocupada=vaga.upper())
            print(estacionamento)
            

            


            # Formata a resposta com as informações da vaga
            dados_vaga = {
                "vaga_ocupada": str(estacionamento.vaga_Ocupada),
                "placa": str(estacionamento.placa),
                "Data Entrada" : str(estacionamento.horario_Entrada.date()),
                "Horario Entrada": estacionamento.horario_Entrada.astimezone(timezone.get_current_timezone()).strftime('%H:%M:%S'),
                "Data Saida Estimada": estacionamento.horario_Saida_Estimada.astimezone(timezone.get_current_timezone()).date(),
                "Horario Saida Estimada": estacionamento.horario_Saida_Estimada.astimezone(timezone.get_current_timezone()).strftime('%H:%M:%S')
            }
        
            return Response(dados_vaga)
            
        except Http404:
            return Response({"error": f"A vaga {vaga} não está ocupada ou não está cadastrada no sistema."}, status=status.HTTP_404_NOT_FOUND)
#Consultar Vagas Disponiveis 
class Estacionamento_Status(APIView):
    def get(self, request):
        total_vagas = Vagas.objects.count()
        vagas_em_uso = Vagas.objects.filter(em_uso=True).count()
        vagas_livres = Vagas.objects.filter(em_uso=False).count()
        vagas_disponiveis = Vagas.objects.filter(em_uso=False)

        # Cria a lista de números das vagas livres
        list_vagas_livres = [vaga.vaga for vaga in vagas_disponiveis]

        estacionamento_vagas = {
            'qtd_total de vagas': total_vagas,
            'qtd_vagas_em_uso': vagas_em_uso,
            'qtd_vagas_livres': vagas_livres,
            'vagas_disponiveis': list_vagas_livres
        }

        return Response(estacionamento_vagas)
        

class VagasCadastradas(APIView):
    def get(self, request):
        total_vagas = Vagas.objects.all()
        vagas_serializer = VagasSerializer(total_vagas, many=True) 

        return Response(vagas_serializer.data)


class Hello_World(APIView):
    def get(self, request):
        return Response("Olá Mundo")
