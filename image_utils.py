# image_utils.py
# Contiene funciones de utilidad para el manejo de imágenes.

import base64

def encode_image_to_base64(image_path: str) -> str:
    """
    Codifica un archivo de imagen a una cadena en formato base64.
    
    Args:
        image_path: La ruta al archivo de imagen.
        
    Returns:
        Una cadena con la imagen codificada en base64.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')