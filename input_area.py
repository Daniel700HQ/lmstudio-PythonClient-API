# input_area.py
# Componente de la UI para la entrada de texto e imagen del usuario.

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class InputArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_path = None

        layout = QVBoxLayout(self)
        text_layout = QHBoxLayout()

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Escribe tu mensaje aquí...")
        self.text_input.setFixedHeight(80)
        text_layout.addWidget(self.text_input)

        self.image_preview = QLabel()
        self.image_preview.setFixedSize(80, 80)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border: 1px solid #565c64; border-radius: 4px;")
        text_layout.addWidget(self.image_preview)

        layout.addLayout(text_layout)

        button_layout = QHBoxLayout()
        self.add_image_button = QPushButton("Añadir Imagen")
        self.send_button = QPushButton("Enviar")

        button_layout.addWidget(self.add_image_button)
        button_layout.addWidget(self.send_button)
        layout.addLayout(button_layout)

        self.add_image_button.clicked.connect(self.add_image)

    def add_image(self):
        """Abre un diálogo para seleccionar un archivo de imagen."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            self.image_preview.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def get_input(self):
        """Devuelve el texto y la ruta de la imagen seleccionada."""
        return self.text_input.toPlainText().strip(), self.image_path

    def clear_input(self):
        """Limpia el área de entrada después de enviar un mensaje."""
        self.text_input.clear()
        self.image_preview.clear()
        self.image_path = None