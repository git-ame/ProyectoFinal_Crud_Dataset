from typing import Dict

class Imagen:
    #Clase para manejar la metadata de las imágenes
    #id en el file_name
    def __init__(self, file_name: str, format: str, size: str, url: str, categoria: str):
        self.file_name = file_name
        self.format = format
        self.size = size
        self.url = url
        self.categoria = categoria

    def to_dict(self) -> Dict:
        #Convierte la metadata a un diccionario
        return {
            'file_name': self.file_name,
            'format': self.format,
            'size': self.size,
            'url': self.url,
            'categoria': self.categoria
        }