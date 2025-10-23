# image_viewer.py
# Un diálogo simple para mostrar una imagen en pantalla completa.

from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageViewer(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visor de Imagen - Presiona 'Esc' para cerrar")
        # Se muestra como una ventana independiente sin bordes
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #000000;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0) # Sin márgenes

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # La política de tamaño permite que el label se expanda para llenar el espacio
        self.image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        
        # Guardamos el pixmap original para poder re-escalarlo si la ventana cambia de tamaño
        self.original_pixmap = pixmap
        
        layout.addWidget(self.image_label)
        
        # Inicia en modo de pantalla completa
        self.showFullScreen()
        
        # Llama a resizeEvent manualmente la primera vez para establecer la imagen
        self.resizeEvent(None)

    def resizeEvent(self, event):
        """
        Se activa cada vez que la ventana cambia de tamaño, incluyendo la primera vez que se muestra.
        Esto asegura que la imagen siempre se re-escala para ajustarse al tamaño actual de la ventana.
        """
        if not self.original_pixmap.isNull():
            # Escala el pixmap ORIGINAL para que se ajuste al tamaño actual del label, manteniendo la proporción.
            scaled_pixmap = self.original_pixmap.scaled(
                self.image_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def keyPressEvent(self, event):
        """Cierra la ventana al presionar la tecla Escape."""
        if event.key() == Qt.Key_Escape:
            self.close()