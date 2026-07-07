"""
Módulo para integração com câmeras IP (RTSP/ONVIF)
"""
import cv2
import threading
import time
from datetime import datetime
from core.models import EventoSeguranca, Camera
from .processamento import DetectorMovimento

class CameraIPManager:
    def __init__(self):
        self.cameras = {}
        self.detector = DetectorMovimento()
        self.threads = []

    def adicionar_camera(self, camera_id, url_rtsp):
        """Adiciona uma câmera para monitoramento"""
        self.cameras[camera_id] = {
            'url': url_rtsp,
            'ativa': True,
            'ultimo_frame': None,
            'eventos': 0
        }
        return True

    def iniciar_monitoramento(self, camera_id):
        """Inicia o monitoramento de uma câmera"""
        if camera_id not in self.cameras:
            return False
        
        def monitorar():
            cap = cv2.VideoCapture(self.cameras[camera_id]['url'])
            if not cap.isOpened():
                print(f"Erro ao abrir câmera {camera_id}")
                return
            
            while self.cameras[camera_id]['ativa']:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(1)
                    continue
                
                # Detectar movimento
                movimento, _ = self.detector.detectar(frame)
                
                if movimento:
                    # Salvar frame como imagem
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    caminho = f'eventos/camera_{camera_id}_{timestamp}.jpg'
                    cv2.imwrite(caminho, frame)
                    
                    # Registrar evento
                    EventoSeguranca.objects.create(
                        tipo='movimento',
                        camera_id=camera_id,
                        descricao=f'Movimento detectado na câmera {camera_id}',
                        imagem=caminho,
                        processado=False
                    )
                    
                    self.cameras[camera_id]['eventos'] += 1
                
                time.sleep(0.1)
            
            cap.release()
        
        thread = threading.Thread(target=monitorar)
        thread.daemon = True
        thread.start()
        self.threads.append(thread)
        
        return True

    def parar_monitoramento(self, camera_id):
        """Para o monitoramento de uma câmera"""
        if camera_id in self.cameras:
            self.cameras[camera_id]['ativa'] = False
            return True
        return False

    def tirar_foto(self, camera_id):
        """Tira uma foto da câmera"""
        if camera_id not in self.cameras:
            return None
        
        cap = cv2.VideoCapture(self.cameras[camera_id]['url'])
        if not cap.isOpened():
            return None
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            caminho = f'eventos/foto_{camera_id}_{timestamp}.jpg'
            cv2.imwrite(caminho, frame)
            return caminho
        
        return None