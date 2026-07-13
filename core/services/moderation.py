from PIL import Image
import io

class ImageModerationService:
    """Serviço simplificado de moderação de imagens"""
    
    def __init__(self):
        self.enabled = True
    
    def moderar_imagem(self, imagem_bytes):
        """Modera uma imagem (versão simplificada)"""
        try:
            # Verificar se a imagem é válida
            img = Image.open(io.BytesIO(imagem_bytes))
            img.verify()
            
            # Verificar tamanho da imagem (evitar imagens gigantes)
            img = Image.open(io.BytesIO(imagem_bytes))
            width, height = img.size
            
            if width > 5000 or height > 5000:
                return {
                    'safe': False,
                    'message': 'Imagem demasiado grande (máx. 5000x5000)'
                }
            
            # Verificar extensões
            format = img.format
            if format not in ['JPEG', 'PNG', 'WEBP']:
                return {
                    'safe': False,
                    'message': f'Formato de imagem não suportado: {format}'
                }
            
            return {'safe': True, 'message': 'Imagem aprovada'}
            
        except Exception as e:
            return {'safe': False, 'message': f'Erro na imagem: {str(e)}'}
    
    def moderar_imagem_arquivo(self, arquivo):
        """Modera uma imagem a partir de um arquivo"""
        try:
            imagem_bytes = arquivo.read()
            return self.moderar_imagem(imagem_bytes)
        except Exception as e:
            return {'safe': False, 'message': f'Erro ao ler imagem: {e}'}