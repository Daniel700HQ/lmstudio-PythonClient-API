# settings_panel.py
# Componente de la UI para configurar la dirección de la API.

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton

class SettingsPanel(QWidget):
    def __init__(self, initial_url, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        api_label = QLabel("Dirección API:")
        self.api_input = QLineEdit(initial_url)
        self.update_api_button = QPushButton("Actualizar")

        layout.addWidget(api_label)
        layout.addWidget(self.api_input)
        layout.addWidget(self.update_api_button)