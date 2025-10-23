# api_client.py
# Gestiona toda la comunicación con la API de LMStudio.

import requests
import json
from PyQt5.QtCore import QObject, pyqtSignal

class APIClient(QObject):
    """
    Cliente para interactuar con la API de LMStudio.
    Emite señales para comunicar el estado de la petición a la UI.
    """
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_base_url):
        super().__init__()
        self.api_base_url = api_base_url

    def set_api_url(self, url):
        """Actualiza la URL base de la API."""
        self.api_base_url = url

    def send_request(self, history):
        """
        Envía una petición POST al endpoint de chat/completions.
        
        Args:
            history: Una lista de mensajes que representa el historial de la conversación.
        """
        headers = {"Content-Type": "application/json"}
        endpoint = f"{self.api_base_url}/chat/completions"

        data = {
            "model": "local-model",  # Este es un valor de ejemplo, LM Studio lo ignora.
            "messages": history,
            "max_tokens": 2048,
            "stream": False
        }

        try:
            response = requests.post(endpoint, headers=headers, json=data, timeout=120)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4xx o 5xx)
            response_json = response.json()
            
            if 'choices' in response_json and len(response_json['choices']) > 0:
                self.response_received.emit(response_json['choices'][0]['message']['content'])
            else:
                self.error_occurred.emit(f"Respuesta inesperada de la API: {response.text}")
        
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"Error de conexión con la API: {e}")
        except json.JSONDecodeError:
            self.error_occurred.emit(f"No se pudo decodificar la respuesta JSON de la API: {response.text}")