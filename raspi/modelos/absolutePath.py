import os

def get_absolute_path():
    # Obtiene la ruta del directorio donde se encuentra el archivo actual (__file__)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construye la ruta absoluta del archivo deseado
    return current_dir
