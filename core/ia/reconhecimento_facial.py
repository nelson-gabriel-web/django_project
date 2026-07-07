"""
Módulo de Reconhecimento Facial com Face Recognition
"""
import face_recognition
import cv2
import numpy as np
from PIL import Image
import os
from django.core.files.storage import default_storage
from core.models import Pessoa, EventoSeguranca

class ReconhecimentoFacial:
    def __init__(self):
        self.encodings_conhecidas = []
        self.nomes_conhecidos = []
        self.carregar_encodings()

    def carregar_encodings(self):
        """Carrega todas as faces conhecidas da base de dados"""
        pessoas = Pessoa.objects.all()
        for pessoa in pessoas:
            if pessoa.foto:
                try:
                    caminho = default_storage.path(pessoa.foto.name)
                    imagem = face_recognition.load_image_file(caminho)
                    encoding = face_recognition.face_encodings(imagem)
                    if encoding:
                        self.encodings_conhecidas.append(encoding[0])
                        self.nomes_conhecidos.append(pessoa.nome)
                except Exception as e:
                    print(f"Erro ao carregar face de {pessoa.nome}: {e}")

    def reconhecer_face(self, imagem_path):
        """Reconhece faces numa imagem"""
        imagem = face_recognition.load_image_file(imagem_path)
        localizacoes = face_recognition.face_locations(imagem)
        encodings = face_recognition.face_encodings(imagem, localizacoes)

        resultados = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(self.encodings_conhecidas, encoding)
            nome = "Desconhecido"
            
            if True in matches:
                primeiro_match = matches.index(True)
                nome = self.nomes_conhecidos[primeiro_match]
            
            resultados.append({
                'nome': nome,
                'conhecido': nome != "Desconhecido"
            })
        
        return resultados

    def processar_evento_com_face(self, evento_id, imagem_path):
        """Processa um evento e tenta reconhecer faces"""
        resultados = self.reconhecer_face(imagem_path)
        
        for resultado in resultados:
            EventoSeguranca.objects.create(
                tipo='face_detectada',
                descricao=f"Face detectada: {resultado['nome']}",
                imagem=imagem_path,
                processado=True
            )
            
            if not resultado['conhecido']:
                # Face desconhecida - enviar alerta
                from .notificacoes import enviar_alerta
                enviar_alerta(evento)
        
        return resultados