import cv2
import numpy as np
import requests
import torch
from datetime import datetime
from ultralytics import YOLO
import time

def ocupar_vaga(vaga):
    url = "http://192.168.18.14:8000/estacionamento_aespi/"
    data = {
        "vaga_Ocupada": vaga,
        "horario_Entrada": datetime.now().isoformat()
    }
    response = requests.post(url, json=data)
    print(f"Vaga ocupada: {vaga}, Status: {response.status_code}, Resposta: {response.json()}")

def delete_vaga(vaga):
    url = f"http://192.168.18.14:8000/estacionamento_aespi/delete/{vaga}"
    response = requests.delete(url)
    print(f"Vaga deletada: {vaga}, Status: {response.status_code}")

# Inicialização da câmera
cam = cv2.VideoCapture(2)  # Utilize 0 para capturar a Webcam

# Configurar dispositivo (GPU ou CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Carregar os modelos
modelo_status = YOLO("best_status.pt")
modelo_identificacao = YOLO("best_identificacao.pt")

if torch.cuda.is_available():
    print("Estou usando a GPU")
else:
    print("Estou usando a CPU")

if cam.isOpened():
    # Classes de detecção
    class_obj_status = ['vaga_livre', 'vaga_ocupada']
    class_obj_identificacao = ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1', 'L1', 'M1', 'N1']

    total_vagas = 14

    # Inicializar dicionário para armazenar o status das vagas
    status_vagas = {vaga: 'vaga_livre' for vaga in class_obj_identificacao}
    ultimo_tempo_detecao = {vaga: time.time() for vaga in class_obj_identificacao}

    # Dicionário para controlar o tempo da última requisição para cada vaga
    ultimo_tempo_requisicao = {vaga: 0 for vaga in class_obj_identificacao}
    intervalo_requisicao = 10  # Intervalo em segundos entre as requisições

    # Estrutura para armazenar os status das vagas
    status_monitoramento = {vaga: [] for vaga in class_obj_identificacao}

    def coordenadas_proximas(box1, box2, threshold=0.5):
        x1_box1, y1_box1, x2_box1, y2_box1 = box1
        x1_box2, y1_box2, x2_box2, y2_box2 = box2

        # Calcula a interseção entre as caixas
        xi1 = max(x1_box1, x1_box2)
        yi1 = max(y1_box1, y1_box2)
        xi2 = min(x2_box1, x2_box2)
        yi2 = min(y2_box1, y2_box2)

        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

        # Área das duas caixas
        box1_area = (x2_box1 - x1_box1) * (y2_box1 - y1_box1)
        box2_area = (x2_box2 - x1_box2) * (y2_box2 - y1_box2)

        # Calcula a união das áreas
        union_area = box1_area + box2_area - inter_area

        # Calcula o índice de sobreposição
        iou = inter_area / union_area

        return iou > threshold

    def ajustar_contraste(frame):
        # Converter a imagem para tons de cinza
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calcular a intensidade média da imagem
        
       
        clipLimit = 1 # Diminui o contraste para evitar superexposição
        
        # Aplicar CLAHE com o clipLimit ajustado
        clahe = cv2.createCLAHE(clipLimit=clipLimit)
        cl = clahe.apply(gray)
    
        # Converter de volta para BGR para manter compatibilidade com outras operações
        return cv2.cvtColor(cl, cv2.COLOR_GRAY2BGR)

    while True:
        validacao, frame = cam.read()

        if not validacao:
            break

        frame = cv2.resize(frame, (800, 600))

        # Ajustar o contraste do frame
        frame = ajustar_contraste(frame)

        # Faz a predição de status no frame atual
        results_status = modelo_status(frame, conf=0.4)
        results_identificacao = modelo_identificacao(frame, conf=0.5)

        # Inicializar contador de vagas ocupadas
        contador_vagas_ocupadas = 0

        # Armazenar as coordenadas e as classes das vagas e dos status detectados
        coordenadas_vagas = []
        coordenadas_status_ocupada = []

        # Processar resultados de identificação (nome das vagas)
        for result in results_identificacao:
            boxes_identificacao = result.boxes
            cls_identificacao = result.boxes.cls
            conf_identificacao = result.boxes.conf  # Confiança

            for box_identificacao, pred_cls_identificacao, conf in zip(boxes_identificacao, cls_identificacao, conf_identificacao):
                x1_id, y1_id, x2_id, y2_id = box_identificacao.xyxy[0].tolist()
                class_index_identificacao = int(pred_cls_identificacao.item())

                if class_index_identificacao < len(class_obj_identificacao):
                    vaga_nome = class_obj_identificacao[class_index_identificacao]
                    coordenadas_vagas.append((vaga_nome, (x1_id, y1_id, x2_id, y2_id)))

                    cv2.putText(frame, f"{vaga_nome}: {conf:.2f}", (int(x1_id), int(y1_id) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Processar resultados de status (livre ou ocupada)
        for result in results_status:
            boxes_status = result.boxes
            cls_status = result.boxes.cls
            conf_status = result.boxes.conf  # Confiança

            for box_status, pred_cls_status, conf in zip(boxes_status, cls_status, conf_status):
                x1_status, y1_status, x2_status, y2_status = box_status.xyxy[0].tolist()
                class_index_status = int(pred_cls_status.item())

                if class_index_status == 1:  # Se for 'vaga_ocupada'
                    coordenadas_status_ocupada.append((x1_status, y1_status, x2_status, y2_status))
                    contador_vagas_ocupadas += 1
                    color = (0, 0, 255)  # Vermelho
                    cv2.rectangle(frame, (int(x1_status), int(y1_status)), (int(x2_status), int(y2_status)), color, 2)

                    cv2.putText(frame, f"Vaga Ocupada: {conf:.2f}", (int(x1_status), int(y1_status) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Comparar coordenadas de vagas identificadas com as vagas ocupadas
        for vaga_nome, coordenadas_vaga in coordenadas_vagas:
            vaga_ocupada = False

            for coordenadas_status in coordenadas_status_ocupada:
                if coordenadas_proximas(coordenadas_vaga, coordenadas_status):
                    status_monitoramento[vaga_nome].append(True)  # Adiciona ocupada
                    vaga_ocupada = True
                    break

            if not vaga_ocupada:
                # Adiciona não ocupada
                status_monitoramento[vaga_nome].append(False)

            # Verifica o número de status ocupados
            if len(status_monitoramento[vaga_nome]) > 10:  # Limita a quantidade de status
                status_monitoramento[vaga_nome].pop(0)  # Remove o mais antigo

            # Avalia o status atual da vaga
            if status_monitoramento[vaga_nome].count(True) > status_monitoramento[vaga_nome].count(False):
                if status_vagas[vaga_nome] != 'vaga_ocupada':
                    status_vagas[vaga_nome] = 'vaga_ocupada'
                    ultimo_tempo_detecao[vaga_nome] = time.time()

                    if time.time() - ultimo_tempo_requisicao[vaga_nome] > intervalo_requisicao:
                        try:
                            ocupar_vaga(vaga_nome)
                        except:
                            print(f" A VAGA {vaga_nome} FOI OCUPADA")
                        ultimo_tempo_requisicao[vaga_nome] = time.time()

            else:
                if status_vagas[vaga_nome] != 'vaga_livre':
                    status_vagas[vaga_nome] = 'vaga_livre'
                    if time.time() - ultimo_tempo_requisicao[vaga_nome] > intervalo_requisicao:
                        try:
                            delete_vaga(vaga_nome)
                        except:
                            print(f" A VAGA {vaga_nome} FOI DELETADA")
                        ultimo_tempo_requisicao[vaga_nome] = time.time()

        vagas_livres = total_vagas - contador_vagas_ocupadas
        cv2.putText(frame, f"Vagas Livres: {vagas_livres}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Vagas Ocupadas: {contador_vagas_ocupadas}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Deteccao de Vagas", frame)

        key = cv2.waitKey(5)
        if key == 27 or cv2.getWindowProperty("Deteccao de Vagas", cv2.WND_PROP_VISIBLE) < 1:
            break

cam.release()
cv2.destroyAllWindows()
