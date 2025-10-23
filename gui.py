# gui.py
# Ventana principal que integra todos los componentes de la aplicación.

import json
import copy 
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox, QDialog, QCheckBox
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt

# Importaciones de los módulos locales
import config
from api_client import APIClient
from image_utils import encode_image_to_base64
from chat_display import ChatDisplay
from input_area import InputArea
from settings_panel import SettingsPanel

# El Worker se encarga de ejecutar la llamada a la API en un hilo separado
# para no congelar la interfaz de usuario.
class Worker(QObject):
    finished = pyqtSignal()
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_client, history):
        super().__init__()
        self.api_client = api_client
        self.history = history

    def run(self):
        # Conecta las señales del APIClient a las del worker
        self.api_client.response_received.connect(self.response_received)
        self.api_client.error_occurred.connect(self.error_occurred)
        self.api_client.send_request(self.history)
        self.finished.emit()

class ChatGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cliente de LMStudio")
        self.setGeometry(100, 100, 800, 700)

        self.history = []
        self.raw_history = []
        self.api_client = APIClient(config.API_BASE_URL)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Creación de los componentes de la UI
        self.settings_panel = SettingsPanel(config.API_BASE_URL)
        self.chat_display = ChatDisplay()
        self.input_area = InputArea()

        control_layout = QHBoxLayout()
        self.clear_chat_button = QPushButton("Limpiar Chat")
        self.view_raw_button = QPushButton("Ver Mensajes Raw")
        control_layout.addWidget(self.clear_chat_button)
        control_layout.addWidget(self.view_raw_button)

        # Añadir widgets al layout principal
        main_layout.addWidget(self.settings_panel)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.chat_display, 1) # El '1' hace que se expanda
        main_layout.addWidget(self.input_area)

        # Conexiones de señales y slots
        self.input_area.send_button.clicked.connect(self.send_message)
        self.clear_chat_button.clicked.connect(self.clear_chat)
        self.view_raw_button.clicked.connect(self.view_raw_messages)
        self.settings_panel.update_api_button.clicked.connect(self.update_api_url)

        self.apply_dark_theme()

    def send_message(self):
        text, image_path = self.input_area.get_input()
        if not text and not image_path:
            return

        user_content = []
        if text:
            user_content.append({"type": "text", "text": text})
        if image_path:
            base64_image = encode_image_to_base64(image_path)
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
            })

        user_message = {"role": "user", "content": user_content}
        self.history.append(user_message)
        self.raw_history.append({"sent": user_message})

        self.chat_display.add_message("user", text, image_path)
        self.input_area.clear_input()

        # Inicia el hilo para la llamada a la API
        self.thread = QThread()
        self.worker = Worker(self.api_client, list(self.history))
        self.worker.moveToThread(self.thread)
        self.worker.response_received.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
        
        self.input_area.send_button.setEnabled(False) # Deshabilita el botón mientras espera

    def handle_response(self, response_text):
        assistant_message = {"role": "assistant", "content": response_text}
        self.history.append(assistant_message)
        if self.raw_history:
            self.raw_history[-1]["received"] = assistant_message
        self.chat_display.add_message("assistant", response_text)
        self.input_area.send_button.setEnabled(True) # Rehabilita el botón

    def handle_error(self, error_message):
        QMessageBox.critical(self, "Error de API", error_message)
        self.input_area.send_button.setEnabled(True) # Rehabilita el botón en caso de error

    def clear_chat(self):
        self.history.clear()
        self.raw_history.clear()
        self.chat_display.clear_chat()
    
    def _get_sanitized_raw_history(self):
        """
        Crea una copia del historial raw y reemplaza el base64 por un placeholder.
        """
        sanitized_history = copy.deepcopy(self.raw_history)
        for entry in sanitized_history:
            if "sent" in entry and "content" in entry["sent"] and isinstance(entry["sent"]["content"], list):
                for content_part in entry["sent"]["content"]:
                    if content_part.get("type") == "image_url":
                        url = content_part.get("image_url", {}).get("url", "")
                        if "base64" in url:
                            content_part["image_url"]["url"] = "<...Contenido de imagen base64 omitido...>"
        return sanitized_history

    def view_raw_messages(self):
        raw_dialog = QDialog(self)
        raw_dialog.setWindowTitle("Mensajes Raw (JSON)")
        raw_dialog.setGeometry(150, 150, 700, 500)
        
        layout = QVBoxLayout(raw_dialog)
        
        # Layout horizontal para los checkboxes de control
        controls_layout = QHBoxLayout()
        
        # Checkbox para mostrar/ocultar base64
        base64_checkbox = QCheckBox("Mostrar contenido de imágenes (base64)")
        base64_checkbox.setChecked(False)
        
        # Checkbox para habilitar/deshabilitar word wrap
        wrap_checkbox = QCheckBox("Habilitar Word Wrap")
        wrap_checkbox.setChecked(False)

        controls_layout.addWidget(base64_checkbox)
        controls_layout.addWidget(wrap_checkbox)
        
        raw_text = QTextEdit()
        raw_text.setReadOnly(True)
        # Estado inicial sin ajuste de línea para mejor rendimiento
        raw_text.setLineWrapMode(QTextEdit.NoWrap)
        
        layout.addLayout(controls_layout)
        layout.addWidget(raw_text)

        # Preparar ambas versiones del historial
        full_history_str = json.dumps(self.raw_history, indent=2, ensure_ascii=False)
        sanitized_history_str = json.dumps(self._get_sanitized_raw_history(), indent=2, ensure_ascii=False)

        # Función para actualizar el texto según el estado de la casilla de base64
        def update_text_view(state):
            if state == Qt.Checked:
                raw_text.setText(full_history_str)
            else:
                raw_text.setText(sanitized_history_str)
        
        # Función para alternar el ajuste de línea (word wrap)
        def toggle_word_wrap(state):
            if state == Qt.Checked:
                raw_text.setLineWrapMode(QTextEdit.WidgetWidth)
            else:
                raw_text.setLineWrapMode(QTextEdit.NoWrap)

        # Conectar las señales de las casillas a sus funciones
        base64_checkbox.stateChanged.connect(update_text_view)
        wrap_checkbox.stateChanged.connect(toggle_word_wrap)
        
        # Establecer el texto inicial (la versión optimizada sin base64)
        raw_text.setText(sanitized_history_str)
        
        raw_dialog.exec_()

    def update_api_url(self):
        new_url = self.settings_panel.api_input.text().strip()
        if not new_url:
            QMessageBox.warning(self, "URL Inválida", "La dirección de la API no puede estar vacía.")
            return
            
        self.api_client.set_api_url(new_url)
        # Actualiza el archivo config.py para persistencia
        try:
            with open("config.py", "w") as f:
                f.write(f'API_BASE_URL = "{new_url}"')
            QMessageBox.information(self, "API Actualizada", f"La dirección de la API es ahora: {new_url}")
        except IOError as e:
            QMessageBox.critical(self, "Error de Archivo", f"No se pudo escribir en config.py: {e}")

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget { 
                background-color: #282c34; 
                color: #ffffff;
            }
            QTextEdit, QLineEdit {
                background-color: #3b4048; 
                color: #ffffff;
                border: 1px solid #2c313a; 
                border-radius: 4px; 
                padding: 5px;
            }
            QPushButton {
                background-color: #61afef; 
                color: #ffffff;
                border: none; 
                padding: 8px 16px; 
                border-radius: 4px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #528baf; 
            }
            QLabel, QCheckBox { 
                color: #ffffff; 
            }
            QScrollArea { 
                border: none; 
            }
            QScrollBar:vertical {
                border: none; 
                background: #2c313a; 
                width: 10px; 
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical { 
                background: #4b5263; 
                min-height: 20px; 
                border-radius: 5px; 
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
                height: 0px; 
            }
            QDialog { 
                background-color: #282c34; 
            }
        """)